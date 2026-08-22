"""Scan flow for the microservices installation (Clark facade).

Mirrors the monolith flow of mdast_scan.main() with the scanyon-native
contract (STG-4451 / STG-4475 / STG-4478):

  engines preflight -> dedup by md5 -> upload -> pre-check gate ->
  create scan (fsm_locked) -> start -> poll (stage, status) -> reports.

The public CLI interface is intentionally unchanged: same flags, same
report file arguments, `--architecture_id`/`--company_id` are accepted
and ignored here.
"""
import json
import logging
import os
import re
import sys
import time

import requests

from mdast_cli.helpers.const import (ACTIVE_STAGES, ANDROID_EXTENSIONS, DEFAULT_ANDROID_ARCHITECTURE,
                                     DEFAULT_IOS_ARCHITECTURE, END_SCAN_TIMEOUT, LONG_TRY, OS_ANDROID,
                                     OS_IOS, PRE_START_STAGES, SLEEP_TIMEOUT, TERMINAL_SCAN_PAIRS, TRY,
                                     UPLOAD_TIMEOUT_ENV_VAR, UPLOAD_TIMEOUT_MAX, UPLOAD_TIMEOUT_MIN,
                                     ENGINE_ACTIVE_STATUS, ScanStage, ScanStageStatus)
from mdast_cli.helpers.exit_codes import ExitCode
from mdast_cli.helpers.helpers import check_app_md5, resolve_report_targets
from mdast_cli_core.factory import architecture_items
from mdast_cli_core.microservices import extract_error_message, mDastMicroservices

logger = logging.getLogger(__name__)

KNOWN_PRECHECK_WARNINGS = {
    'empty_profile': 'Scan profile has no enabled modules',
    'no_compatible_devices': 'No compatible devices for the required OS version',
    'application_not_found': 'Application is not found on the platform',
    'precheck_unavailable': 'Pre-check dependencies are temporarily unavailable, retry later',
    'architecture_unsupported': 'Platform/OS version pair is not supported by this installation',
}

# Transient downstream failures (facade/scanyon/pepper) are retried while polling
# and downloading, so a rolling restart of a backend mid-scan does not kill a
# long CI job. ~5 min budget per call covers a typical k8s rolling restart.
# 429 (Too Many Requests) is included: scanyon rate-limits with a 429, and backing
# off is the correct response, not an immediate abort.
POLL_TRANSIENT_RETRIES = 30
POLL_TRANSIENT_CODES = (429, 502, 503, 504)
# upload has its own (shorter) transient budget: a busy/redeploying/rate-limited
# upload path returns 429/502/503, worth a few retries, but not the full 5 min.
UPLOAD_TRANSIENT_RETRIES = 3
UPLOAD_TRANSIENT_CODES = (429, 502, 503)

# Strip C0/C1 control chars from server-controlled strings before logging, keeping
# only TAB (\x09). CRUCIALLY this includes LF (\x0a) and CR (\x0d): otherwise a
# hostile/compromised server could embed a newline in `message`/`package_name` and
# forge an extra log line in CI output (CWE-117 log injection).
_CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0a-\x1f\x7f-\x9f]')


def sanitize(value):
    """Strip control/ANSI chars (incl. CR/LF) from server strings before logging.

    A hostile/compromised server could embed ANSI escapes or CR/LF into fields
    like `message`/`package_name` to forge log lines / poison CI logs; neutralise
    them. Only TAB survives from the control range.
    """
    return _CONTROL_CHARS_RE.sub('', str(value))


def resolve_platform(app_file):
    """ANDROID/IOS from the application file extension."""
    _, extension = os.path.splitext(app_file)
    if extension.lower() in ANDROID_EXTENSIONS:
        return OS_ANDROID
    if extension.lower() == '.ipa':
        return OS_IOS


def resolve_ms_os_version(architectures, platform):
    """Choose a deterministic Scanyon OS version for a CLI scan."""
    architectures = architecture_items(architectures)
    if architectures is None:
        return None

    candidates = [
        architecture for architecture in architectures
        if isinstance(architecture, dict)
        and str(architecture.get('type', '')).upper() == platform
        and str(architecture.get('os_version', '')).strip()
    ]
    if not candidates:
        return None

    preferred_name = {
        OS_ANDROID: DEFAULT_ANDROID_ARCHITECTURE,
        OS_IOS: DEFAULT_IOS_ARCHITECTURE,
    }.get(platform)
    selected = next(
        (architecture for architecture in candidates if architecture.get('name') == preferred_name),
        candidates[0],
    )
    return str(selected['os_version']).strip()
    return None


def render_precheck_warning(warning):
    """One human-readable line per pre-check warning: known text + raw payload.

    Unknown warning types are rendered generically: the contract explicitly
    allows backward-compatible extension of the type set (DEC-666-04). Payload is
    JSON-escaped so server-controlled content cannot inject terminal sequences.
    """
    warning_type = sanitize(warning.get('type', 'unknown'))
    payload = warning.get('payload') or {}
    text = KNOWN_PRECHECK_WARNINGS.get(warning.get('type'), 'Scan pre-check warning')
    payload_str = json.dumps(payload, ensure_ascii=False) if payload else ''
    return f'[{warning_type}] {text}{" " + payload_str if payload_str else ""}'


def scan_pair(scan):
    return scan.get('stage'), scan.get('status')


def is_terminal(scan):
    return scan_pair(scan) in TERMINAL_SCAN_PAIRS


def is_success(scan):
    stage, status = scan_pair(scan)
    return stage == ScanStage.SUCCESS and status in (ScanStageStatus.COMPLETE,
                                                     ScanStageStatus.PARTIAL_COMPLETE)


def resolve_upload_timeout():
    """Optional server-side upload_timeout override via env (no new CLI flags)."""
    raw = os.environ.get(UPLOAD_TIMEOUT_ENV_VAR)
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        logger.warning(f'Ignoring invalid {UPLOAD_TIMEOUT_ENV_VAR}={raw!r} (expected integer)')
        return None
    clamped = max(UPLOAD_TIMEOUT_MIN, min(UPLOAD_TIMEOUT_MAX, value))
    if clamped != value:
        logger.warning(f'{UPLOAD_TIMEOUT_ENV_VAR}={value} is out of range, using {clamped}')
    return clamped


def _exit_on_http_error(resp, action, exit_code=ExitCode.SCAN_FAILED):
    message = sanitize(extract_error_message(resp))
    if resp.status_code in (401, 403):
        logger.error(f'{action}: authorization failed (HTTP {resp.status_code}): {message}. '
                     'Check the organization CLI token (issued in the platform UI).')
        sys.exit(ExitCode.AUTH_ERROR)
    logger.error(f'{action} failed (HTTP {resp.status_code}): {message}')
    sys.exit(exit_code)


def _json_or_exit(resp, action, exit_code=ExitCode.NETWORK_ERROR):
    """Parse a 2xx response body as JSON or exit cleanly.

    A 2xx with a non-JSON body (e.g. an nginx/Envoy HTML stub, or a 204 with no
    body) must not crash with a raw traceback; it is a network/gateway problem,
    not INTERNAL_ERROR.
    """
    try:
        return resp.json()
    except ValueError:
        logger.error(f'{action}: server returned HTTP {resp.status_code} with a non-JSON body '
                     f'(unexpected gateway/proxy response).')
        sys.exit(exit_code)


def _retry_request(call, action, retries, exit_code=ExitCode.NETWORK_ERROR):
    """Call `call()` (returns a Response), retrying transient 5xx/network errors.

    Non-transient HTTP errors and exhausted transient retries exit via
    `_exit_on_http_error`. Returns the successful (2xx) Response.
    """
    last_resp = None
    for attempt in range(retries):
        try:
            resp = call()
        except requests.RequestException as ex:
            logger.warning(f'{action} request failed ({type(ex).__name__}), '
                           f'retry {attempt + 1}/{retries}')
            if attempt + 1 < retries:
                time.sleep(SLEEP_TIMEOUT)
            continue
        if 200 <= resp.status_code < 300:
            return resp
        last_resp = resp
        if resp.status_code in POLL_TRANSIENT_CODES and attempt + 1 < retries:
            logger.warning(f'{action} returned {resp.status_code} (transient), '
                           f'retry {attempt + 1}/{retries}')
            time.sleep(SLEEP_TIMEOUT)
            continue
        break
    if last_resp is not None:
        _exit_on_http_error(last_resp, action, exit_code)
    logger.error(f'{action} failed after {retries} attempts (network)')
    sys.exit(exit_code)


def _get_scan(mdast, scan_id):
    """Poll scan state, tolerating transient downstream failures."""
    resp = _retry_request(lambda: mdast.get_scan_info(scan_id),
                          f'Getting scan info for scan {scan_id}', POLL_TRANSIENT_RETRIES)
    return _json_or_exit(resp, f'Getting scan info for scan {scan_id}')


def run_precheck_gate(mdast, md5, profile_id, testcase_id, scan_type, os_version=None):
    """Gate model (DEC-671-05): any warning blocks the scan with a non-zero exit.

    A transient gateway failure (429/502/503/504) or a raw network error is NOT a
    policy block: it is retried and, if it persists, exits NETWORK_ERROR(6) (the CI
    "retry" signal) rather than PRECHECK_BLOCKED(8). The scan is still not created
    in that case, so the gate stays fail-closed either way.
    """
    resp = None
    for attempt in range(UPLOAD_TRANSIENT_RETRIES):
        try:
            resp = mdast.precheck_scan(md5, profile_id, testcase_id, scan_type, os_version=os_version)
        except requests.RequestException as ex:
            logger.warning(f'Scan pre-check request failed ({type(ex).__name__}), '
                           f'retry {attempt + 1}/{UPLOAD_TRANSIENT_RETRIES}')
            resp = None
            if attempt + 1 < UPLOAD_TRANSIENT_RETRIES:
                time.sleep(SLEEP_TIMEOUT)
            continue
        if resp.status_code in POLL_TRANSIENT_CODES and attempt + 1 < UPLOAD_TRANSIENT_RETRIES:
            logger.warning(f'Scan pre-check returned {resp.status_code} (transient), '
                           f'retry {attempt + 1}/{UPLOAD_TRANSIENT_RETRIES}')
            time.sleep(SLEEP_TIMEOUT)
            continue
        break
    if resp is None:
        logger.error('Scan pre-check could not be completed (network). This is retryable '
                     'infrastructure, not a policy block.')
        sys.exit(ExitCode.NETWORK_ERROR)
    if resp.status_code in (401, 403):
        _exit_on_http_error(resp, 'Scan pre-check')  # -> AUTH_ERROR
    if resp.status_code == 404:
        _exit_on_http_error(resp, 'Scan pre-check (profile lookup)')  # -> SCAN_FAILED
    if resp.status_code == 422 and profile_id is None:
        # Auto-created-profile scan (no --profile_id): the profile does not exist
        # yet, so pre-check cannot run against it. Skipping is intentional interim
        # behaviour; platform-side validation still runs at scan creation.
        logger.warning('Scan pre-check skipped: no --profile_id given (profile is '
                       'auto-created at scan start); platform validates at creation.')
        return
    if resp.status_code in POLL_TRANSIENT_CODES:
        # transient gateway/rate-limit that outlived the retry budget: retryable infra,
        # not a deliberate policy block -> NETWORK_ERROR(6), consistent with the rest.
        message = sanitize(extract_error_message(resp))
        logger.error(f'Scan pre-check unavailable (HTTP {resp.status_code}): {message}. '
                     'Retryable infrastructure, not a policy block.')
        sys.exit(ExitCode.NETWORK_ERROR)
    if resp.status_code != 200:
        message = sanitize(extract_error_message(resp))
        logger.error(f'Scan pre-check is unavailable (HTTP {resp.status_code}): {message}')
        sys.exit(ExitCode.PRECHECK_BLOCKED)
    warnings = (_json_or_exit(resp, 'Scan pre-check') or {}).get('warnings') or []
    if not warnings:
        logger.info('Scan pre-check passed, no warnings')
        return
    logger.error('Scan pre-check returned blocking warnings, scan will not be created:')
    for warning in warnings:
        print(render_precheck_warning(warning), file=sys.stderr)
    sys.exit(ExitCode.PRECHECK_BLOCKED)


def run_microservices_flow(arguments, url, token, app_file, user_agent=None, verify=True):
    """Full scan flow against the microservices installation. Exits the process.

    Wrapped so a bare network error surfaces as NETWORK_ERROR(6), consistent with
    the rest of the flow, instead of a traceback + INTERNAL_ERROR(1).

    Note there is no appstore_app_md5 parameter (unlike the monolith path): the
    App Store downloader rewrites the .ipa after download (adds iTunesMetadata /
    sinf), so the Apple-store md5 differs from the file actually uploaded. The
    microservices flow always keys dedup/precheck/create off the local file md5,
    which is also what upload sends - so an App Store (iOS) build uploads and
    scans on the microservices installation exactly like any other .ipa (F1).
    """
    try:
        _run_microservices_flow(arguments, url, token, app_file, user_agent, verify)
    except requests.RequestException as ex:
        logger.error(f'Network error talking to the microservices installation '
                     f'({type(ex).__name__}): {ex}')
        sys.exit(ExitCode.NETWORK_ERROR)


def _run_microservices_flow(arguments, url, token, app_file, user_agent, verify):
    profile_id = arguments.profile_id
    project_id = arguments.project_id
    testcase_id = arguments.testcase_id

    if arguments.appium_script_path:
        logger.error('Appium scans are not supported on the microservices installation '
                     '(--appium_script_path). Use a recorded test case (--testcase_id) instead.')
        sys.exit(ExitCode.INVALID_ARGS)
    if arguments.cr_report:
        logger.error('CR report generation (--cr_report) is not supported on the '
                     'microservices installation.')
        sys.exit(ExitCode.INVALID_ARGS)
    if arguments.architecture_id is not None:
        logger.warning('--architecture_id is ignored on the microservices installation: '
                       'the platform resolves the architecture from application metadata')

    mdast = mDastMicroservices(url, token, arguments.company_id,
                               user_agent=user_agent, verify=verify)

    architectures_resp = mdast.get_architectures()
    if architectures_resp.status_code != 200:
        _exit_on_http_error(architectures_resp, 'Getting architectures', ExitCode.NETWORK_ERROR)
    architectures_payload = _json_or_exit(architectures_resp, 'Getting architectures')
    architectures = architecture_items(architectures_payload)
    if architectures is None:
        logger.error('Getting architectures: unexpected response shape '
                     '(expected a list or paginated items envelope)')
        sys.exit(ExitCode.NETWORK_ERROR)
    logger.info(f'Supported architectures: {architectures}')

    platform = resolve_platform(app_file)
    if platform is None:
        logger.error(f'Cannot resolve platform (Android/iOS) from file extension: {app_file}')
        sys.exit(ExitCode.INVALID_ARGS)

    os_version = resolve_ms_os_version(architectures, platform)
    if os_version is None:
        logger.error(f'Cannot create scan - no supported OS version for platform {platform}')
        sys.exit(ExitCode.SCAN_FAILED)
    logger.info(f'Selected OS version for {platform}: {sanitize(os_version)}')

    if testcase_id is not None:
        testcase_resp = mdast.get_testcase(testcase_id)
        if testcase_resp.status_code == 200:
            testcase_os = str((_json_or_exit(testcase_resp, 'Getting test case') or {}).get('os', '')).upper()
            if testcase_os and testcase_os != platform:
                logger.error(f'Test case {testcase_id} is recorded for {testcase_os}, '
                             f'but the application file is for {platform}')
                sys.exit(ExitCode.INVALID_ARGS)
        elif testcase_resp.status_code in (401, 403):
            _exit_on_http_error(testcase_resp, f'Getting test case {testcase_id}')
        else:
            logger.warning(f'Cannot get test case {testcase_id} '
                           f'(HTTP {testcase_resp.status_code}), continuing')

    engines_resp = mdast.get_engines()
    if engines_resp.status_code != 200:
        _exit_on_http_error(engines_resp, 'Getting engines', ExitCode.NETWORK_ERROR)
    engines = _json_or_exit(engines_resp, 'Getting engines')
    if not isinstance(engines, list):
        logger.error('Getting engines: unexpected response shape (expected a list)')
        sys.exit(ExitCode.NETWORK_ERROR)
    active_engines = [engine for engine in engines
                      if isinstance(engine, dict)
                      and str(engine.get('type', '')).upper() == platform
                      and str(engine.get('status', '')).upper() == ENGINE_ACTIVE_STATUS]
    if not active_engines:
        logger.error(f'Cannot create scan - no active engine for platform {platform}')
        sys.exit(ExitCode.SCAN_FAILED)

    # F1: single md5 for the whole flow — the md5 of the file actually uploaded.
    # For appstore the CLI rewrites the ipa (adds iTunesMetadata/sinf) after
    # download, so the Apple store md5 differs from what is uploaded; dedup /
    # precheck / create must all use the local file's md5, which upload also sends.
    logger.info('Check if this version of application was already uploaded..')
    app_md5 = check_app_md5(app_file).lower()
    dedup_resp = mdast.check_app_md5(None, app_md5)
    if dedup_resp.status_code != 200:
        _exit_on_http_error(dedup_resp, 'Application dedup check', ExitCode.NETWORK_ERROR)
    found_apps = _json_or_exit(dedup_resp, 'Application dedup check')
    application = found_apps[0] if isinstance(found_apps, list) and found_apps else None
    if application:
        logger.info('This app was uploaded before, application id is: '
                    f"{application.get('id')}, package name: {sanitize(application.get('package_name'))}, "
                    f"version: {sanitize(application.get('version_name'))}, md5: {sanitize(application.get('md5'))}")
    else:
        logger.info('This is new application or new version')
        logger.info('Uploading application to server..')
        upload_timeout = resolve_upload_timeout()
        application = _upload_application(mdast, app_file, upload_timeout)

    app_id = application.get('id')
    if not app_id:
        logger.error(f'Application response has no id: {sanitize(application)}')
        sys.exit(ExitCode.SCAN_FAILED)

    precheck_type = 'AUTO' if testcase_id is not None else 'MANUAL'
    run_precheck_gate(mdast, app_md5, profile_id, testcase_id, precheck_type, os_version=os_version)

    logger.info(f'Creating scan for application {sanitize(app_id)}')
    if testcase_id is not None:
        create_resp = mdast.create_auto_scan(
            project_id, profile_id, app_md5, None, testcase_id, os_version=os_version,
        )
        scan_type = 'auto_stingray'
    else:
        create_resp = mdast.create_manual_scan(project_id, profile_id, app_md5, os_version=os_version)
        scan_type = 'manual'
    if create_resp.status_code not in (200, 201):
        _exit_on_http_error(create_resp, 'Creating scan')
    scan = _json_or_exit(create_resp, 'Creating scan')
    scan_id = scan.get('id')
    if not scan_id:
        logger.error(f'Something went wrong while creating scan: {scan}')
        sys.exit(ExitCode.SCAN_FAILED)
    logger.info('Project and profile were created/found successfully. '
                f"Project id: {(scan.get('project') or {}).get('id')}, "
                f"profile id: {(scan.get('profile') or {}).get('id')}")
    logger.info(f'Scan was created successfully. Scan id: {scan_id}')

    logger.info(f'Start scan with id {scan_id}')
    start_resp = mdast.start_scan(scan_id)
    if start_resp.status_code == 409:
        # POST /scans/{id}/start/ is not idempotent: a facade retry (network/timeout
        # after the first call already unlocked the scan) surfaces as 409 "not in
        # initial state" even though the scan did start. Confirm by state before failing.
        current = _get_scan(mdast, scan_id)
        if current.get('stage') != ScanStage.CREATED:
            logger.warning(f'Start returned 409 but scan {scan_id} is already past initial '
                           f'state ({scan_pair(current)}) - treating as started (facade retry).')
        else:
            _exit_on_http_error(start_resp, f'Starting scan {scan_id}')
    elif start_resp.status_code != 200:
        _exit_on_http_error(start_resp, f'Starting scan {scan_id}')

    if arguments.nowait:
        logger.info('Scan successfully started. Don`t wait for end, exit with zero code')
        sys.exit(ExitCode.SUCCESS)

    try_count = LONG_TRY if arguments.long_wait else TRY

    logger.info('Scan started successfully.')
    scan = _get_scan(mdast, scan_id)
    logger.info(f'Current scan state: {scan_pair(scan)}')

    count = 0
    while scan.get('stage') in PRE_START_STAGES and count < try_count:
        logger.info(f'Try to get scan status for scan id {scan_id}. Count number {count}')
        scan = _get_scan(mdast, scan_id)
        logger.info(f'Current scan state: {scan_pair(scan)}')
        count += 1
        if scan.get('stage') in PRE_START_STAGES:
            logger.info(f'Wait {SLEEP_TIMEOUT} seconds and try again')
            time.sleep(SLEEP_TIMEOUT)

    if scan.get('stage') not in ACTIVE_STAGES | {ScanStage.SUCCESS, ScanStage.FAIL}:
        logger.error(f'Error with scan id {scan_id}. Scan did not start, '
                     f'current state: {scan_pair(scan)}, message: {sanitize(scan.get("message"))}')
        sys.exit(ExitCode.SCAN_FAILED)

    if scan_type == 'manual' and not is_terminal(scan) and scan.get('stage') != ScanStage.STOP:
        logger.info(f'This is a scan without a test case, '
                    f'lets wait for {END_SCAN_TIMEOUT} seconds and stop it.')
        time.sleep(END_SCAN_TIMEOUT)
        try:
            stop_resp = mdast.stop_scan(scan_id)
        except requests.RequestException as ex:
            logger.error(f'Stopping scan {scan_id} request failed ({type(ex).__name__})')
            sys.exit(ExitCode.NETWORK_ERROR)
        if stop_resp.status_code == 200:
            logger.info(f'Scan {scan_id} was requested to stop (stopped by CLI after '
                        f'{END_SCAN_TIMEOUT} seconds, as in the manual scan flow)')
        elif stop_resp.status_code == 409:
            logger.info(f'Scan {scan_id} is not in a stoppable state anymore, continuing')
        else:
            _exit_on_http_error(stop_resp, f'Stopping scan {scan_id}')

    logger.info(f"Scan {scan_id} is started now. Let's wait until the scan is finished")
    count = 0
    while not is_terminal(scan) and count < try_count:
        logger.info(f'Try to get scan status for scan id {scan_id}. Count number {count}')
        scan = _get_scan(mdast, scan_id)
        logger.info(f'Current scan state: {scan_pair(scan)}')
        count += 1
        if not is_terminal(scan):
            logger.info(f'Wait {SLEEP_TIMEOUT} seconds and try again')
            time.sleep(SLEEP_TIMEOUT)

    if not is_terminal(scan):
        logger.error(f'Scan {scan_id} did not reach a terminal state within the wait budget '
                     f'(last state {scan_pair(scan)}). Increase timeout with --long_wait.')
        sys.exit(ExitCode.SCAN_FAILED)
    if not is_success(scan):
        logger.error(f'Scan {scan_id} finished with state {scan_pair(scan)}, '
                     f'message: {sanitize(scan.get("message"))}. Exit with error status code.')
        sys.exit(ExitCode.SCAN_FAILED)
    if scan.get('status') == ScanStageStatus.PARTIAL_COMPLETE:
        logger.warning(f'Scan {scan_id} finished partially complete '
                       f'(some modules did not run): {sanitize(scan.get("message"))}')

    download_reports(mdast, scan_id, arguments)


def _upload_application(mdast, app_file, upload_timeout):
    """Upload with transient retry; friendly message on server-side parse timeout.

    Retries both transient HTTP (502/503) and raw network errors: a rolling
    restart of the upload path can drop the connection outright, not only answer
    502. The server keys uploads by md5, so re-sending the same build is
    idempotent (a lost-response upload is de-duplicated server-side).
    """
    last_resp = None
    for attempt in range(UPLOAD_TRANSIENT_RETRIES):
        try:
            resp = mdast.upload_application(app_file, upload_timeout=upload_timeout)
        except requests.RequestException as ex:
            logger.warning(f'Uploading application request failed ({type(ex).__name__}), '
                           f'retry {attempt + 1}/{UPLOAD_TRANSIENT_RETRIES}')
            if attempt + 1 < UPLOAD_TRANSIENT_RETRIES:
                time.sleep(SLEEP_TIMEOUT)
            continue
        if 200 <= resp.status_code < 300:
            # Accept any 2xx (not just 201): a facade/gateway may answer 200 for an
            # already-registered build, and the rest of the flow (poll/create) already
            # treats 2xx as success.
            application = _json_or_exit(resp, 'Uploading application')
            logger.info(f"Application uploaded successfully. Application id: {application.get('id')}")
            return application
        if resp.status_code == 504:
            # Gateway timeout: the synchronous wait elapsed but the platform keeps
            # parsing. Re-running finds the build via md5 dedup. This is retryable
            # infra, not a bad scan -> NETWORK_ERROR (the CI "retry" signal).
            logger.error('Application parsing did not finish in time (504). The upload is '
                         'processed asynchronously - retry the same command later, the file '
                         f'will not be re-uploaded. {UPLOAD_TIMEOUT_ENV_VAR} env var can raise '
                         f'the wait (max {UPLOAD_TIMEOUT_MAX} seconds).')
            sys.exit(ExitCode.NETWORK_ERROR)
        last_resp = resp
        if resp.status_code in UPLOAD_TRANSIENT_CODES and attempt + 1 < UPLOAD_TRANSIENT_RETRIES:
            logger.warning(f'Uploading application returned {resp.status_code} (transient), '
                           f'retry {attempt + 1}/{UPLOAD_TRANSIENT_RETRIES}')
            time.sleep(SLEEP_TIMEOUT)
            continue
        break
    if last_resp is not None:
        if last_resp.status_code in UPLOAD_TRANSIENT_CODES:
            # gateway 5xx / rate-limit that outlived the retry budget: retryable infra
            logger.error(f'Uploading application failed: transient status {last_resp.status_code} '
                         f'persisted after {UPLOAD_TRANSIENT_RETRIES} retries.')
            sys.exit(ExitCode.NETWORK_ERROR)
        _exit_on_http_error(last_resp, 'Uploading application')
    logger.error(f'Uploading application failed after {UPLOAD_TRANSIENT_RETRIES} attempts '
                 f'(network). For large builds raise the wait with {UPLOAD_TIMEOUT_ENV_VAR} '
                 f'(seconds, max {UPLOAD_TIMEOUT_MAX}).')
    sys.exit(ExitCode.NETWORK_ERROR)


def download_reports(mdast, scan_id, arguments):
    """Report step (STG-4478): files are written to CLI-chosen paths.

    Format selection is shared with the monolith flow (--report_format, default
    pdf, scan-id default names). Reports are downloaded independently and are
    soft-fail: the scan already finished SUCCESS, so a report render failure (e.g.
    Pepper 502, a separate microservice) must not turn a green scan red or block
    the other report format. Content-Disposition from the server is deliberately
    ignored - the local file name is a CLI argument.
    """
    targets = resolve_report_targets(arguments, scan_id)
    failures = []

    if 'pdf' in targets:
        target = targets['pdf']
        logger.info(f'Create and download pdf report for scan {scan_id} to file {target}.')
        resp = _download_report(mdast.download_report, scan_id, 'PDF report')
        if resp is None:
            failures.append('PDF')
        else:
            with open(target, 'wb') as f:
                f.write(resp.content)
            logger.info(f'PDF report for scan {scan_id} saved to {target}.')

    if 'json' in targets:
        target = targets['json']
        logger.info(f'Download JSON summary report for scan {scan_id} to file {target}.')
        resp = _download_report(mdast.download_scan_json_result, scan_id, 'JSON report')
        if resp is None:
            failures.append('JSON')
        else:
            try:
                payload = resp.json()
            except ValueError:
                logger.error('JSON report: server returned a non-JSON body; saving raw bytes.')
                with open(target, 'wb') as f:
                    f.write(resp.content)
            else:
                with open(target, 'w') as fp:
                    json.dump(payload, fp, indent=4, ensure_ascii=False)
            logger.info(f'JSON report for scan {scan_id} saved to {target}.')

    if failures:
        # Soft-fail: scan succeeded; report render is a downstream (Pepper) issue.
        logger.warning(f'Scan {scan_id} finished successfully, but these reports could not be '
                       f'downloaded (report service issue, not scan failure): {", ".join(failures)}. '
                       'Retry the report download later.')


def _download_report(fetch, scan_id, label):
    """Download one report with transient retry. Returns Response or None (soft-fail)."""
    last = None
    for attempt in range(POLL_TRANSIENT_RETRIES):
        try:
            resp = fetch(scan_id)
        except requests.RequestException as ex:
            logger.warning(f'{label} request failed ({type(ex).__name__}), '
                           f'retry {attempt + 1}/{POLL_TRANSIENT_RETRIES}')
            if attempt + 1 < POLL_TRANSIENT_RETRIES:
                time.sleep(SLEEP_TIMEOUT)
            continue
        if resp.status_code == 200:
            return resp
        last = resp
        if resp.status_code in POLL_TRANSIENT_CODES and attempt + 1 < POLL_TRANSIENT_RETRIES:
            logger.warning(f'{label} returned {resp.status_code} (transient), '
                           f'retry {attempt + 1}/{POLL_TRANSIENT_RETRIES}')
            time.sleep(SLEEP_TIMEOUT)
            continue
        break
    if last is not None:
        logger.error(f'{label} download failed (HTTP {last.status_code}): '
                     f'{sanitize(extract_error_message(last))}')
    return None
