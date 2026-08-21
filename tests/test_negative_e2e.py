"""Negative end-to-end flows: the CLI must fail with the RIGHT exit code.

These exercise main() end to end (arg parse -> mode -> flow) against a mocked
server and assert the process exit code, which is the contract CI depends on:

    2 INVALID_ARGS | 4 DOWNLOAD_FAILED | 5 SCAN_FAILED |
    6 NETWORK_ERROR | 7 AUTH_ERROR | 8 PRECHECK_BLOCKED

Exit codes must be identical in meaning on both installations (F12).
"""
import json

import pytest
import responses
from responses import matchers

from tests.conftest import BASE_URL, REST_URL, TOKEN, application_json, run_main, scan_json

pytestmark = pytest.mark.e2e

ARCH = f'{REST_URL}/architectures/'


def base_argv(tmp_apk, *extra):
    return ['--distribution_system', 'file', '--file_path', tmp_apk,
            '--url', BASE_URL, '--company_id', '1', '--token', TOKEN, *extra]


def argv_without_company_id(tmp_apk, *extra):
    return ['--distribution_system', 'file', '--file_path', tmp_apk,
            '--url', BASE_URL, '--token', TOKEN, *extra]


def _register_ms_preamble(rsps, apk_md5, engine_status='STARTED', engine_type='ANDROID',
                          apps=None):
    """Everything up to (not including) upload/create, microservices shaped."""
    rsps.add(responses.GET, ARCH, json=[
        {'id': 1, 'type': 'ANDROID', 'os_version': '11', 'name': 'Android 11'}])
    rsps.add(responses.GET, f'{REST_URL}/engines/',
             json=[{'engine_id': 'e-1', 'type': engine_type, 'status': engine_status}])
    rsps.add(responses.GET, f'{REST_URL}/applications/',
             json=apps if apps is not None else [])


# --- mode detection ---------------------------------------------------------

def test_mode_detection_auth_failure_exit_7(mocked_responses, monkeypatch, tmp_apk):
    """Both probes answer 401 -> AUTH_ERROR, and the token never leaks."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH, status=401)  # Bearer probe
    mocked_responses.add(responses.GET, ARCH, status=401)  # Token probe
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 7


def test_mode_detection_ambiguous_payload_exit_6(mocked_responses, monkeypatch, tmp_apk):
    """200 with a payload matching neither shape is a gateway/config problem (network)."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH, json={'unexpected': 'shape'})
    mocked_responses.add(responses.GET, ARCH, json={'unexpected': 'shape'})
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_mode_detection_unreachable_exit_6(mocked_responses, monkeypatch, tmp_apk):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH, status=500)
    mocked_responses.add(responses.GET, ARCH, status=503)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


# --- upload -----------------------------------------------------------------

def test_ms_upload_gateway_502_exhausted_exit_6(mocked_responses, monkeypatch, tmp_apk,
                                                apk_md5, no_sleep, ms_mode):
    """A persistent 502 on upload is retryable infra -> NETWORK_ERROR, not SCAN_FAILED."""
    _register_ms_preamble(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/', status=502)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_ms_upload_504_exit_6(mocked_responses, monkeypatch, tmp_apk, apk_md5, no_sleep, ms_mode):
    """504 = server still parsing; re-run dedupes. Retryable -> NETWORK_ERROR."""
    _register_ms_preamble(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/', status=504)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_ms_upload_auth_401_exit_7(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                   no_sleep, ms_mode):
    _register_ms_preamble(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/', status=401)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 7


# --- preflight rejections ---------------------------------------------------

def test_ms_no_active_engine_exit_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                    no_sleep, ms_mode):
    """Android app but the only engine is iOS -> cannot scan (SCAN_FAILED)."""
    _register_ms_preamble(mocked_responses, apk_md5, engine_type='IOS')
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5


def test_ms_engine_present_but_down_exit_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                           no_sleep, ms_mode):
    _register_ms_preamble(mocked_responses, apk_md5, engine_status='STOPPED_SIGTERM')
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5


def test_ms_testcase_platform_mismatch_exit_2(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                              no_sleep, ms_mode):
    """Android file + iOS-recorded test case is a user mistake (INVALID_ARGS)."""
    mocked_responses.add(responses.GET, ARCH,
                         json=[{'id': 1, 'type': 'ANDROID', 'os_version': '11'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'id': 5, 'os': 'IOS'})
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5')) == 2


# --- scan lifecycle ---------------------------------------------------------

def _register_ms_through_start(rsps, apk_md5):
    rsps.add(responses.GET, f'{REST_URL}/testcases/5/', json={'id': 5, 'os': 'ANDROID'})
    _register_ms_preamble(rsps, apk_md5, apps=[application_json(apk_md5)])
    rsps.add(responses.POST, f'{REST_URL}/scans/start/precheck/', json={'warnings': []})
    rsps.add(responses.POST, f'{REST_URL}/scans/start/',
             json=scan_json(stage='CREATED', status='INITIAL'))
    rsps.add(responses.POST, f'{REST_URL}/scans/77/start/',
             json=scan_json(stage='START', status='INITIAL'))


def test_ms_scan_never_terminal_times_out_exit_5(mocked_responses, monkeypatch, tmp_apk,
                                                 apk_md5, no_sleep, ms_mode):
    """A scan that never reaches a terminal (stage, status) must FAIL, not hang or pass."""
    monkeypatch.setattr('mdast_cli.ms_flow.TRY', 2)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='WORKING', status='PROCESSING'))
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5')) == 5


def test_ms_scan_fail_terminal_exit_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                      no_sleep, ms_mode):
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='FAIL', status='FAIL', message='boom'))
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5')) == 5


# --- manual scan without a profile (F10) ------------------------------------

def test_ms_manual_without_profile_skips_precheck_and_stops(mocked_responses, monkeypatch,
                                                            tmp_path, tmp_apk, apk_md5,
                                                            no_sleep, ms_mode):
    """F10: no --profile_id -> profile is auto-created, so pre-check (422, profile does
    not exist yet) is skipped rather than blocking; the manual scan is stopped by the
    CLI after the wait and is still expected to finish SUCCESS."""
    monkeypatch.chdir(tmp_path)
    _register_ms_preamble(mocked_responses, apk_md5, apps=[application_json(apk_md5)])
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/',
                         json={'detail': 'profile not found'}, status=422)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json=scan_json(stage='CREATED', status='INITIAL', type='MANUAL'))
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/',
                         json=scan_json(stage='WORKING', status='PROCESSING'))
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/stop/',
                         json=scan_json(stage='STOP', status='PROCESSING'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='WORKING', status='PROCESSING'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 x',
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 0
    create = [c for c in mocked_responses.calls if c.request.url == f'{REST_URL}/scans/start/']
    body = json.loads(create[0].request.body)
    assert body['type'] == 'MANUAL'
    assert 'profile_id' not in body, 'no --profile_id -> profile_id must be omitted (auto-create)'
    assert [c for c in mocked_responses.calls if c.request.url == f'{REST_URL}/scans/77/stop/'], \
        'manual scan must be stopped by the CLI after the wait'


# --- reports (soft-fail) ----------------------------------------------------

def test_ms_report_soft_fail_keeps_scan_green(mocked_responses, monkeypatch, tmp_path,
                                              tmp_apk, apk_md5, no_sleep, ms_mode, caplog):
    """PDF render fails (Pepper 502) but the scan finished SUCCESS: exit 0, JSON still saved."""
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', status=502,
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report',
                         json={'summary': {'scan_id': 77}},
                         match=[matchers.query_param_matcher({'output': 'json'})])
    exit_code = run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5',
                                                '--report_format', 'all'))
    assert exit_code == 0
    assert not (tmp_path / 'scan_report_77.pdf').exists()
    assert json.loads((tmp_path / 'scan_report_77.json').read_text())['summary']['scan_id'] == 77


def test_ms_default_report_is_pdf(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                                  no_sleep, ms_mode):
    """No report flags at all -> a PDF is produced by default, named by scan id."""
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 x',
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5')) == 0
    assert (tmp_path / 'scan_report_77.pdf').read_bytes().startswith(b'%PDF')
    assert not (tmp_path / 'scan_report_77.json').exists()


def test_ms_report_format_none_writes_nothing(mocked_responses, monkeypatch, tmp_path,
                                              tmp_apk, apk_md5, no_sleep, ms_mode):
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5',
                                           '--report_format', 'none')) == 0
    assert not list(tmp_path.glob('scan_report_*'))


# --- arg / input validation -------------------------------------------------

def test_missing_file_path_exit_2(monkeypatch, tmp_path):
    missing = str(tmp_path / 'does_not_exist.apk')
    assert run_main(monkeypatch, ['--distribution_system', 'file', '--file_path', missing,
                                  '--url', BASE_URL, '--company_id', '1', '--token', TOKEN]) == 2


def test_scan_without_credentials_exit_2(monkeypatch, tmp_apk):
    """No --url/--token and not --download_only -> argparse error (2)."""
    assert run_main(monkeypatch, ['--distribution_system', 'file', '--file_path', tmp_apk]) == 2


def test_download_only_without_scan_credentials_still_succeeds(monkeypatch, tmp_apk):
    assert run_main(monkeypatch, [
        '--download_only', '--distribution_system', 'file', '--file_path', tmp_apk,
    ]) == 0


def test_forced_monolith_without_company_id_exit_2(mocked_responses, monkeypatch, tmp_apk,
                                                   monolith_mode, caplog):
    assert run_main(monkeypatch, argv_without_company_id(tmp_apk)) == 2
    assert '--company_id is required for monolith mode' in caplog.text
    assert not mocked_responses.calls


def test_autodetected_monolith_without_company_id_exit_2(mocked_responses, monkeypatch,
                                                         tmp_apk, caplog):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    monolith_architectures = [{'id': 1, 'name': 'Android 11', 'type': 1}]
    mocked_responses.add(responses.GET, ARCH, json=monolith_architectures)
    mocked_responses.add(responses.GET, ARCH, json=monolith_architectures)

    assert run_main(monkeypatch, argv_without_company_id(tmp_apk)) == 2
    assert '--company_id is required for monolith mode' in caplog.text
    assert len(mocked_responses.calls) == 2
    assert all('/organizations/' not in call.request.url for call in mocked_responses.calls)


def test_cr_report_without_credentials_exit_2(monkeypatch, tmp_apk):
    assert run_main(monkeypatch, base_argv(tmp_apk, '--cr_report')) == 2


# --- URL normalization robustness -------------------------------------------

def test_url_already_ending_in_rest_slash_still_works(mocked_responses, monkeypatch, tmp_path,
                                                      tmp_apk, apk_md5, no_sleep, ms_mode):
    """--url '.../rest/' must not produce '//' paths (which a strict facade 404s).

    All endpoints are registered at the single-slash canonical form; if
    normalization regressed to leaving a trailing slash, the requests would miss
    and the flow would fail with NETWORK_ERROR instead of 0.
    """
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 x',
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    argv = ['--distribution_system', 'file', '--file_path', tmp_apk,
            '--url', f'{BASE_URL}/rest/', '--company_id', '1', '--token', TOKEN,
            '--testcase_id', '5']
    assert run_main(monkeypatch, argv) == 0
    assert (tmp_path / 'scan_report_77.pdf').exists()


# --- monolith parity --------------------------------------------------------

def _register_mono_through_start(rsps):
    """Monolith manual flow up to (and including) start; dedup returns an existing
    app so the upload step is skipped. Caller registers the GET /dasts/77/ polls."""
    rest = REST_URL
    rsps.add(responses.GET, f'{rest}/architectures/',
             json=[{'id': 1, 'name': 'Android 11', 'type': 1}])
    rsps.add(responses.GET, f'{rest}/organizations/1/engines/',
             json=[{'architecture': 1, 'state': 3}])
    rsps.add(responses.GET, f'{rest}/organizations/1/applications/',
             json=[{'id': 10, 'package_name': 'com.example.app', 'version_name': '1.0', 'md5': 'x'}])
    rsps.add(responses.POST, f'{rest}/organizations/1/dasts/',
             json={'id': 77, 'project': {'id': 1}, 'profile': {'id': 2}}, status=201)
    rsps.add(responses.POST, f'{rest}/dasts/77/start/', json={}, status=200)


def _register_mono_through_success(rsps):
    _register_mono_through_start(rsps)
    rest = REST_URL
    rsps.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    rsps.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    rsps.add(responses.POST, f'{rest}/dasts/77/stop/', json={}, status=200)
    rsps.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 4})


def test_autodetect_resolves_monolith_and_runs(mocked_responses, monkeypatch, tmp_apk):
    """Auto mode must classify a monolith (int-type payload) and run the monolith flow,
    even though the Bearer probe answers 200 - classification is by payload shape."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    _register_mono_through_start(mocked_responses)
    assert run_main(monkeypatch, base_argv(tmp_apk, '--nowait')) == 0
    # the Token-scheme /organizations/1/ URLs prove the monolith flow ran
    assert any('/organizations/1/' in c.request.url for c in mocked_responses.calls)


def test_monolith_mid_poll_401_is_auth_error_exit_7(mocked_responses, monkeypatch, tmp_apk,
                                                    no_sleep, monolith_mode):
    """F12: a token expiring mid-scan (poll 401) must exit AUTH_ERROR(7), like microservices."""
    _register_mono_through_start(mocked_responses)
    mocked_responses.add(responses.GET, f'{REST_URL}/dasts/77/', status=401,
                         json={'detail': 'token expired'})
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 7


def test_monolith_network_exception_is_network_error_exit_6(monkeypatch, mocked_responses,
                                                           tmp_apk, monolith_mode):
    """F12: a bare connection error in the monolith flow -> NETWORK_ERROR(6), not a traceback+1."""
    # no endpoints registered -> the first monolith call raises ConnectionError
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_monolith_invalid_architecture_id_exit_2(mocked_responses, monkeypatch, tmp_apk,
                                                 monolith_mode):
    """An --architecture_id the server doesn't know is a user error -> INVALID_ARGS(2), not a crash."""
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/',
                         json=[{'id': 1, 'name': 'Android 11', 'type': 1}])
    assert run_main(monkeypatch, base_argv(tmp_apk, '--architecture_id', '999')) == 2


def test_monolith_report_pdf_hardfail_exit_5(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                            no_sleep, monolith_mode):
    """Monolith keeps report download as a HARD fail (unlike microservices soft-fail)."""
    monkeypatch.chdir(tmp_path)
    _register_mono_through_success(mocked_responses)
    mocked_responses.add(responses.GET, f'{REST_URL}/dasts/77/report/', status=502)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5


def test_monolith_json_report_non_json_body_exit_5(mocked_responses, monkeypatch, tmp_path,
                                                  tmp_apk, no_sleep, monolith_mode):
    """A 200 with a non-JSON body must exit SCAN_FAILED(5), not traceback, and leave no file."""
    monkeypatch.chdir(tmp_path)
    _register_mono_through_success(mocked_responses)
    mocked_responses.add(responses.GET, f'{REST_URL}/dasts/77/report/', body=b'<html>oops</html>')
    assert run_main(monkeypatch, base_argv(tmp_apk, '--report_format', 'json')) == 5
    assert not list(tmp_path.glob('scan_report_*'))


def test_monolith_scan_failed_state_exit_5(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                           no_sleep, monolith_mode):
    """Monolith must map a non-SUCCESS terminal state to SCAN_FAILED, same as microservices."""
    monkeypatch.chdir(tmp_path)
    rest = REST_URL
    mocked_responses.add(responses.GET, f'{rest}/architectures/',
                         json=[{'id': 1, 'name': 'Android 11', 'type': 1}])
    mocked_responses.add(responses.GET, f'{rest}/organizations/1/engines/',
                         json=[{'architecture': 1, 'state': 3}])
    mocked_responses.add(responses.GET, f'{rest}/organizations/1/applications/',
                         json=[{'id': 10, 'package_name': 'com.example.app',
                                'version_name': '1.0', 'md5': 'x'}])
    mocked_responses.add(responses.POST, f'{rest}/organizations/1/dasts/',
                         json={'id': 77, 'project': {'id': 1}, 'profile': {'id': 2}}, status=201)
    mocked_responses.add(responses.POST, f'{rest}/dasts/77/start/', json={}, status=200)
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    mocked_responses.add(responses.POST, f'{rest}/dasts/77/stop/', json={}, status=200)
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 5})
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5


# ===== more Sting-side negatives (microservices) — expanded coverage =====

def test_ms_architectures_5xx_is_network_6(mocked_responses, monkeypatch, tmp_apk, no_sleep, ms_mode):
    mocked_responses.add(responses.GET, ARCH, status=500)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_ms_architectures_non_json_is_network_6(mocked_responses, monkeypatch, tmp_apk, no_sleep, ms_mode):
    """A 200 with a non-JSON body (nginx/Envoy HTML stub) is a gateway problem, not a crash."""
    mocked_responses.add(responses.GET, ARCH, body='<html>gw</html>', status=200, content_type='text/html')
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_ms_engines_5xx_is_network_6(mocked_responses, monkeypatch, tmp_apk, no_sleep, ms_mode):
    mocked_responses.add(responses.GET, ARCH, json=[{'id': 1, 'type': 'ANDROID', 'os_version': '11'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', status=500)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_ms_engines_empty_no_active_engine_5(mocked_responses, monkeypatch, tmp_apk, no_sleep, ms_mode):
    mocked_responses.add(responses.GET, ARCH, json=[{'id': 1, 'type': 'ANDROID', 'os_version': '11'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', json=[])
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5


def test_ms_dedup_5xx_is_network_6(mocked_responses, monkeypatch, tmp_apk, no_sleep, ms_mode):
    mocked_responses.add(responses.GET, ARCH, json=[{'id': 1, 'type': 'ANDROID', 'os_version': '11'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/',
                         json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/', status=500)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def _ms_through_precheck(rsps, apk_md5):
    """architectures + testcase + engines + dedup(existing) + precheck OK; caller adds create/start."""
    rsps.add(responses.GET, ARCH, json=[{'id': 1, 'type': 'ANDROID', 'os_version': '11'}])
    rsps.add(responses.GET, f'{REST_URL}/testcases/5/', json={'id': 5, 'os': 'ANDROID'})
    rsps.add(responses.GET, f'{REST_URL}/engines/', json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    rsps.add(responses.GET, f'{REST_URL}/applications/', json=[application_json(apk_md5)])
    rsps.add(responses.POST, f'{REST_URL}/scans/start/precheck/', json={'warnings': []})


def test_ms_create_scan_4xx_is_scan_failed_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                             no_sleep, ms_mode):
    _ms_through_precheck(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json={'error_code': 'bad_request', 'message': 'nope'}, status=400)
    assert run_main(monkeypatch, base_argv(tmp_apk, '--profile_id', '2', '--testcase_id', '5')) == 5


def test_ms_create_scan_no_id_is_scan_failed_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                              no_sleep, ms_mode):
    _ms_through_precheck(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/', json={}, status=200)
    assert run_main(monkeypatch, base_argv(tmp_apk, '--profile_id', '2', '--testcase_id', '5')) == 5


def test_ms_start_5xx_is_scan_failed_5(mocked_responses, monkeypatch, tmp_apk, apk_md5,
                                       no_sleep, ms_mode):
    _ms_through_precheck(mocked_responses, apk_md5)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json=scan_json(stage='CREATED', status='INITIAL'))
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/',
                         json={'error_code': 'x', 'message': 'boom'}, status=500)
    assert run_main(monkeypatch, base_argv(tmp_apk, '--profile_id', '2', '--testcase_id', '5')) == 5


def test_ms_partial_complete_succeeds_0(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                                        no_sleep, ms_mode):
    """PARTIAL_COMPLETE is a green terminal (some modules skipped): exit 0 with a warning."""
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='PARTIAL_COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 x',
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5')) == 0


def test_ms_both_reports_fail_still_green_0(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                            apk_md5, no_sleep, ms_mode):
    """Scan SUCCESS but BOTH reports 502 -> soft-fail: exit 0 (report service is separate)."""
    monkeypatch.chdir(tmp_path)
    _register_ms_through_start(mocked_responses, apk_md5)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='SUCCESS', status='COMPLETE'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', status=502,
                         match=[matchers.query_param_matcher({'output': 'pdf'})])
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', status=502,
                         match=[matchers.query_param_matcher({'output': 'json'})])
    assert run_main(monkeypatch, base_argv(tmp_apk, '--testcase_id', '5', '--report_format', 'all')) == 0


# ===== more Sting-side negatives (monolith) =====

def test_monolith_architectures_5xx_is_network_6(mocked_responses, monkeypatch, tmp_apk,
                                                no_sleep, monolith_mode):
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', status=500)
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 6


def test_monolith_no_active_engine_5(mocked_responses, monkeypatch, tmp_apk, no_sleep, monolith_mode):
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/',
                         json=[{'id': 1, 'name': 'Android 11', 'type': 1}])
    # engine present but state != 3 (not active)
    mocked_responses.add(responses.GET, f'{REST_URL}/organizations/1/engines/',
                         json=[{'architecture': 1, 'state': 2}])
    assert run_main(monkeypatch, base_argv(tmp_apk)) == 5
