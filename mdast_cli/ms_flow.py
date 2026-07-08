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
import sys
import time

from mdast_cli.helpers.const import (ACTIVE_STAGES, ANDROID_EXTENSIONS, END_SCAN_TIMEOUT, LONG_TRY, OS_ANDROID,
                                     OS_IOS, PRE_START_STAGES, SLEEP_TIMEOUT, TERMINAL_SCAN_PAIRS, TRY,
                                     UPLOAD_TIMEOUT_ENV_VAR, UPLOAD_TIMEOUT_MAX, UPLOAD_TIMEOUT_MIN,
                                     ENGINE_ACTIVE_STATUS, ScanStage, ScanStageStatus)
from mdast_cli.helpers.exit_codes import ExitCode
from mdast_cli.helpers.helpers import check_app_md5
from mdast_cli_core.microservices import extract_error_message, mDastMicroservices

logger = logging.getLogger(__name__)

KNOWN_PRECHECK_WARNINGS = {
    'empty_profile': 'Scan profile has no enabled modules',
    'no_compatible_devices': 'No compatible devices for the required OS version',
    'application_not_found': 'Application is not found on the platform',
    'precheck_unavailable': 'Pre-check dependencies are temporarily unavailable, retry later',
    'architecture_unsupported': 'Platform/OS version pair is not supported by this installation',
}


def resolve_platform(app_file):
    """ANDROID/IOS from the application file extension."""
    _, extension = os.path.splitext(app_file)
    if extension in ANDROID_EXTENSIONS:
        return OS_ANDROID
    if extension == '.ipa':
        return OS_IOS
    return None


def render_precheck_warning(warning):
    """One human-readable line per pre-check warning: known text + raw payload.

    Unknown warning types are rendered generically: the contract explicitly
    allows backward-compatible extension of the type set (DEC-666-04).
    """
    warning_type = str(warning.get('type', 'unknown'))
    payload = warning.get('payload') or {}
    text = KNOWN_PRECHECK_WARNINGS.get(warning_type, 'Scan pre-check warning')
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
    message = extract_error_message(resp)
    if resp.status_code in (401, 403):
        logger.error(f'{action}: authorization failed (HTTP {resp.status_code}): {message}. '
                     'Check the organization CLI token (issued in the platform UI).')
        sys.exit(ExitCode.AUTH_ERROR)
    logger.error(f'{action} failed (HTTP {resp.status_code}): {message}')
    sys.exit(exit_code)


def _get_scan(mdast, scan_id):
    resp = mdast.get_scan_info(scan_id)
    if resp.status_code != 200:
        _exit_on_http_error(resp, f'Getting scan info for scan {scan_id}',
                            ExitCode.NETWORK_ERROR)
    return resp.json()


def run_precheck_gate(mdast, md5, profile_id, testcase_id, scan_type):
    """Gate model (DEC-671-05): any warning blocks the scan with a non-zero exit."""
    resp = mdast.precheck_scan(md5, profile_id, testcase_id, scan_type)
    if resp.status_code == 404:
        _exit_on_http_error(resp, 'Scan pre-check (profile lookup)')
    if resp.status_code == 422 and profile_id is None:
        # Installation does not yet accept pre-check without profile_id
        # (scanyon change pending); skipping is a documented interim behavior.
        logger.warning('Scan pre-check skipped: this installation requires profile_id '
                       'for pre-check and no --profile_id was given')
        return
    if resp.status_code != 200:
        message = extract_error_message(resp)
        logger.error(f'Scan pre-check is unavailable (HTTP {resp.status_code}): {message}')
        sys.exit(ExitCode.PRECHECK_BLOCKED)
    warnings = (resp.json() or {}).get('warnings') or []
    if not warnings:
        logger.info('Scan pre-check passed, no warnings')
        return
    logger.error('Scan pre-check returned blocking warnings, scan will not be created:')
    for warning in warnings:
        print(render_precheck_warning(warning), file=sys.stderr)
    sys.exit(ExitCode.PRECHECK_BLOCKED)


def run_microservices_flow(arguments, url, token, app_file, appstore_app_md5, user_agent=None,
                           verify=False):
    """Full scan flow against the microservices installation. Exits the process."""
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
    logger.info(f'Supported architectures: {architectures_resp.json()}')

    platform = resolve_platform(app_file)
    if platform is None:
        logger.error(f'Cannot resolve platform (Android/iOS) from file extension: {app_file}')
        sys.exit(ExitCode.INVALID_ARGS)

    if testcase_id is not None:
        testcase_resp = mdast.get_testcase(testcase_id)
        if testcase_resp.status_code == 200:
            testcase_os = str(testcase_resp.json().get('os', '')).upper()
            if testcase_os and testcase_os != platform:
                logger.error(f'Test case {testcase_id} is recorded for {testcase_os}, '
                             f'but the application file is for {platform}')
                sys.exit(ExitCode.INVALID_ARGS)
        else:
            logger.warning(f'Cannot get test case {testcase_id} '
                           f'(HTTP {testcase_resp.status_code}), continuing')

    engines_resp = mdast.get_engines()
    if engines_resp.status_code != 200:
        _exit_on_http_error(engines_resp, 'Getting engines', ExitCode.NETWORK_ERROR)
    engines = engines_resp.json()
    active_engines = [engine for engine in engines
                      if str(engine.get('type', '')).upper() == platform
                      and str(engine.get('status', '')).upper() == ENGINE_ACTIVE_STATUS]
    if not active_engines:
        logger.error(f'Cannot create scan - no active engine for platform {platform}')
        sys.exit(ExitCode.SCAN_FAILED)

    logger.info('Check if this version of application was already uploaded..')
    app_md5 = (appstore_app_md5 or check_app_md5(app_file)).lower()
    dedup_resp = mdast.check_app_md5(None, app_md5)
    if dedup_resp.status_code != 200:
        _exit_on_http_error(dedup_resp, 'Application dedup check', ExitCode.NETWORK_ERROR)
    found_apps = dedup_resp.json()
    if found_apps:
        application = found_apps[0]
        logger.info(f"This app was uploaded before, application id is: {application['id']}, "
                    f"package name: {application['package_name']}, "
                    f"version: {application['version_name']}, md5: {application['md5']}")
    else:
        logger.info('This is new application or new version')
        logger.info('Uploading application to server..')
        upload_resp = mdast.upload_application(app_file, upload_timeout=resolve_upload_timeout())
        if upload_resp.status_code != 201:
            if upload_resp.status_code == 504:
                logger.error('Application parsing did not finish in time (504). The upload is '
                             'processed asynchronously - retry the same command later, the file '
                             f'will not be re-uploaded. {UPLOAD_TIMEOUT_ENV_VAR} env var can '
                             'raise the wait (max 300 seconds).')
                sys.exit(ExitCode.SCAN_FAILED)
            _exit_on_http_error(upload_resp, 'Uploading application')
        application = upload_resp.json()
        logger.info(f"Application uploaded successfully. Application id: {application['id']}")

    precheck_type = 'AUTO' if testcase_id is not None else 'MANUAL'
    run_precheck_gate(mdast, app_md5, profile_id, testcase_id, precheck_type)

    logger.info(f"Creating scan for application {application['id']}")
    if testcase_id is not None:
        create_resp = mdast.create_auto_scan(project_id, profile_id, app_md5, None, testcase_id)
        scan_type = 'auto_stingray'
    else:
        create_resp = mdast.create_manual_scan(project_id, profile_id, app_md5)
        scan_type = 'manual'
    if create_resp.status_code not in (200, 201):
        _exit_on_http_error(create_resp, 'Creating scan')
    scan = create_resp.json()
    if not scan.get('id'):
        logger.error(f'Something went wrong while creating scan: {scan}')
        sys.exit(ExitCode.SCAN_FAILED)
    scan_id = scan['id']
    logger.info(f"Project and profile was created/found successfully. "
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
                     f'current state: {scan_pair(scan)}, message: {scan.get("message")}')
        sys.exit(ExitCode.SCAN_FAILED)

    if scan_type == 'manual' and not is_terminal(scan) and scan.get('stage') != ScanStage.STOP:
        logger.info(f'This is a scan without a test case, '
                    f'lets wait for {END_SCAN_TIMEOUT} seconds and stop it.')
        time.sleep(END_SCAN_TIMEOUT)
        stop_resp = mdast.stop_scan(scan_id)
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

    if not is_success(scan):
        logger.error(f'Scan {scan_id} finished with state {scan_pair(scan)}, '
                     f'message: {scan.get("message")}. Exit with error status code.')
        sys.exit(ExitCode.SCAN_FAILED)
    if scan.get('status') == ScanStageStatus.PARTIAL_COMPLETE:
        logger.warning(f'Scan {scan_id} finished partially complete: {scan.get("message")}')

    download_reports(mdast, scan_id, arguments)


def download_reports(mdast, scan_id, arguments):
    """Report step (STG-4478): files are written to the user-provided paths.

    Content-Disposition from the server is deliberately ignored: the local
    file name is a CLI argument and must not be controlled by the server.
    """
    pdf_report_file_name = arguments.pdf_report_file_name
    json_summary_file_name = arguments.summary_report_json_file_name

    if pdf_report_file_name:
        logger.info(f'Create and download pdf report for scan with id {scan_id} '
                    f'to file {pdf_report_file_name}.')
        pdf_report = mdast.download_report(scan_id)
        if pdf_report.status_code != 200:
            _exit_on_http_error(pdf_report, 'PDF report downloading')
        pdf_report_file_name = pdf_report_file_name if pdf_report_file_name.endswith(
            '.pdf') else f'{pdf_report_file_name}.pdf'
        with open(pdf_report_file_name, 'wb') as f:
            f.write(pdf_report.content)
        logger.info(f'Report for scan {scan_id} successfully created and available at path: '
                    f'{pdf_report_file_name}.')

    if json_summary_file_name:
        logger.info(f'Download JSON summary report for scan with id {scan_id} '
                    f'to file {json_summary_file_name}.')
        json_report = mdast.download_scan_json_result(scan_id)
        if json_report.status_code != 200:
            _exit_on_http_error(json_report, 'JSON summary report downloading')
        json_file_name = json_summary_file_name if json_summary_file_name.endswith(
            '.json') else f'{json_summary_file_name}.json'
        with open(json_file_name, 'w') as fp:
            json.dump(json_report.json(), fp, indent=4, ensure_ascii=False)
        logger.info(f'JSON report for scan {scan_id} successfully created and available '
                    f'at path: {json_file_name}.')
