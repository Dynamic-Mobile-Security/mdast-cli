"""Smoke tests: full CLI flows against a mocked server.

The microservices flow follows the acceptance scenario of STG-4475:
architectures -> engines -> dedup/upload -> pre-check gate -> create (fsm_locked)
-> start -> polling to a terminal (stage, status) -> reports.
The monolith flow is pinned as a regression guard (dual-mode must not break it).
"""
import json
import os

import pytest
import responses

from tests.conftest import BASE_URL, REST_URL, TOKEN, application_json, run_main, scan_json

pytestmark = pytest.mark.smoke


def register_ms_happy_path(rsps, apk_md5, with_testcase=True):
    rsps.add(responses.GET, f'{REST_URL}/architectures/', json=[
        {'id': 1, 'type': 1, 'os_version': '11', 'name': 'Android 11', 'description': 'API 30'},
    ])
    if with_testcase:
        rsps.add(responses.GET, f'{REST_URL}/testcases/5/', json={'id': 5, 'os': 'ANDROID'})
    rsps.add(responses.GET, f'{REST_URL}/engines/', json=[
        {'engine_id': 'e-1', 'type': 'ANDROID', 'status': 'STARTED'},
        {'engine_id': 'e-2', 'type': 'IOS', 'status': 'STOPPED_SIGTERM'},
    ])
    rsps.add(responses.GET, f'{REST_URL}/applications/', json=[])
    rsps.add(responses.POST, f'{REST_URL}/applications/upload_info/',
             json=application_json(apk_md5), status=201)
    rsps.add(responses.POST, f'{REST_URL}/scans/start/precheck/', json={'warnings': []})
    rsps.add(responses.POST, f'{REST_URL}/scans/start/',
             json=scan_json(stage='CREATED', status='INITIAL'), status=200)
    rsps.add(responses.POST, f'{REST_URL}/scans/77/start/',
             json=scan_json(stage='START', status='INITIAL'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/',
             json=scan_json(stage='WORKING', status='PROCESSING'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/',
             json=scan_json(stage='SUCCESS', status='COMPLETE'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 fake',
             content_type='application/pdf',
             headers={'Content-Disposition': 'attachment; filename="dast_77.pdf"'})
    rsps.add(responses.GET, f'{REST_URL}/scans/77/report',
             json={'summary': {'scan_id': 77}, 'defect_summary': {}, 'requirements': [],
                   'defects': []},
             headers={'Content-Disposition': 'attachment; filename="dast_77.json"'})


def ms_argv(tmp_apk, with_testcase=True):
    argv = ['--distribution_system', 'file', '--file_path', tmp_apk,
            '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
            '--profile_id', '2',
            '--pdf_report_file_name', 'scan_report_pdf',
            '--summary_report_json_file_name', 'scan_report_json']
    if with_testcase:
        argv += ['--testcase_id', '5']
    return argv


def test_ms_full_flow_success(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                              no_sleep, ms_mode):
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5)
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk))
    assert exit_code == 0
    assert (tmp_path / 'scan_report_pdf.pdf').read_bytes().startswith(b'%PDF')
    report = json.loads((tmp_path / 'scan_report_json.json').read_text())
    assert report['summary']['scan_id'] == 77
    # create scan body follows the scanyon-native contract
    create_calls = [c for c in mocked_responses.calls
                    if c.request.url == f'{REST_URL}/scans/start/']
    body = json.loads(create_calls[0].request.body)
    assert body['md5'] == apk_md5
    assert body['type'] == 'AUTO'
    assert body['fsm_locked'] is True


def test_ms_full_flow_with_autodetect(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                      apk_md5, no_sleep):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5)
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk))
    assert exit_code == 0


def test_ms_manual_flow_stops_scan(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                                   no_sleep, ms_mode):
    """Scan without a test case keeps the manual semantics: wait, stop, expect SUCCESS."""
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5, with_testcase=False)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/stop/',
                         json=scan_json(stage='STOP', status='PROCESSING'))
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk, with_testcase=False))
    assert exit_code == 0
    stop_calls = [c for c in mocked_responses.calls
                  if c.request.url == f'{REST_URL}/scans/77/stop/']
    assert stop_calls, 'manual flow must request scan stop'


def test_ms_precheck_gate_blocks(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                                 no_sleep, ms_mode, capsys):
    monkeypatch.chdir(tmp_path)
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'os': 'ANDROID'})
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/',
                         json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/',
                         json=[application_json(apk_md5)])
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/', json={
        'warnings': [{'type': 'empty_profile', 'payload': {}}]})
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk))
    assert exit_code == 8
    assert '[empty_profile]' in capsys.readouterr().err
    scan_creates = [c for c in mocked_responses.calls
                    if c.request.url == f'{REST_URL}/scans/start/']
    assert not scan_creates, 'scan must not be created when pre-check blocks'


def test_ms_scan_fail_state(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                            no_sleep, ms_mode):
    monkeypatch.chdir(tmp_path)
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'os': 'ANDROID'})
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/',
                         json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/',
                         json=[application_json(apk_md5)])
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/',
                         json={'warnings': []})
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json=scan_json(stage='CREATED', status='INITIAL'))
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/',
                         json=scan_json(stage='START'))
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='FAIL', status='FAIL',
                                        message='All modules failed'))
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk))
    assert exit_code == 5


def test_ms_start_409_facade_retry_is_tolerated(mocked_responses, monkeypatch, tmp_path,
                                                tmp_apk, apk_md5, no_sleep, ms_mode):
    """POST /scans/{id}/start/ is not idempotent: a facade retry after the first
    (successful) call returns 409, but the scan did start. CLI must confirm by state
    and continue, not fail."""
    monkeypatch.chdir(tmp_path)
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'os': 'ANDROID'})
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/',
                         json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/',
                         json=[application_json(apk_md5)])
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/',
                         json={'warnings': []})
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json=scan_json(stage='CREATED', status='INITIAL'))
    # start returns 409 (retry after first unlock succeeded)
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/',
                         json={'error_code': 'bad_request', 'message': 'недоступны'}, status=409)
    # but the scan is already past initial - 409 must be tolerated
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='START', status='INITIAL'))
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk) + ['--nowait'])
    assert exit_code == 0


def test_ms_start_409_real_conflict_fails(mocked_responses, monkeypatch, tmp_path,
                                          tmp_apk, apk_md5, no_sleep, ms_mode):
    """A genuine 409 (scan still in CREATED) must NOT be masked - CLI fails."""
    monkeypatch.chdir(tmp_path)
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'os': 'ANDROID'})
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/',
                         json=[{'type': 'ANDROID', 'status': 'STARTED'}])
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/',
                         json=[application_json(apk_md5)])
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/',
                         json={'warnings': []})
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/',
                         json=scan_json(stage='CREATED', status='INITIAL'))
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/',
                         json={'error_code': 'bad_request', 'message': 'x'}, status=409)
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='CREATED', status='INITIAL'))
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk) + ['--nowait'])
    assert exit_code == 5


def test_ms_appium_rejected(monkeypatch, tmp_apk, ms_mode):
    exit_code = run_main(monkeypatch, [
        '--distribution_system', 'file', '--file_path', tmp_apk,
        '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
        '--appium_script_path', '/tmp/script.py'])
    assert exit_code == 2


def test_ms_cr_report_rejected(monkeypatch, tmp_apk, ms_mode):
    exit_code = run_main(monkeypatch, [
        '--distribution_system', 'file', '--file_path', tmp_apk,
        '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
        '--cr_report', '--stingray_login', 'x', '--stingray_password', 'y'])
    assert exit_code == 2


def test_monolith_regression_flow(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                  no_sleep, monolith_mode):
    """The pre-dual-mode monolith flow must keep working byte-for-byte."""
    monkeypatch.chdir(tmp_path)
    rest = REST_URL
    mocked_responses.add(responses.GET, f'{rest}/architectures/', json=[
        {'id': 1, 'name': 'Android 11', 'type': 1},
        {'id': 3, 'name': 'iOS 14', 'type': 2},
    ])
    mocked_responses.add(responses.GET, f'{rest}/organizations/1/engines/', json=[
        {'architecture': 1, 'state': 3},
    ])
    mocked_responses.add(responses.GET, f'{rest}/organizations/1/applications/', json=[])
    mocked_responses.add(responses.POST, f'{rest}/organizations/1/applications/',
                         json={'id': 10}, status=201)
    mocked_responses.add(responses.POST, f'{rest}/organizations/1/dasts/',
                         json={'id': 77, 'project': {'id': 1}, 'profile': {'id': 2}},
                         status=201)
    mocked_responses.add(responses.POST, f'{rest}/dasts/77/start/', json={}, status=200)
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 2})
    mocked_responses.add(responses.POST, f'{rest}/dasts/77/stop/', json={}, status=200)
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/', json={'id': 77, 'state': 4})
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/report/', body=b'%PDF-1.4 mono')
    mocked_responses.add(responses.GET, f'{rest}/dasts/77/report/', json={'summary': {}})
    exit_code = run_main(monkeypatch, [
        '--distribution_system', 'file', '--file_path', tmp_apk,
        '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
        '--pdf_report_file_name', 'mono_pdf',
        '--summary_report_json_file_name', 'mono_json'])
    assert exit_code == 0
    assert (tmp_path / 'mono_pdf.pdf').read_bytes().startswith(b'%PDF')
    assert (tmp_path / 'mono_json.json').exists()
    # monolith URL shapes preserved: organization segment and Token scheme
    engine_calls = [c for c in mocked_responses.calls
                    if '/organizations/1/engines/' in c.request.url]
    assert engine_calls
    assert engine_calls[0].request.headers['Authorization'] == f'Token {TOKEN}'
