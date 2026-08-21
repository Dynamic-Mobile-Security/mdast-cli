"""Unit/contract tests for the microservices client (Clark facade URLs, bodies, headers)."""
import json

import pytest
import responses

from mdast_cli_core.microservices import file_md5, mDastMicroservices
from tests.conftest import REST_URL, TOKEN

pytestmark = [pytest.mark.unit, pytest.mark.contract]


@pytest.fixture
def client():
    return mDastMicroservices(REST_URL, TOKEN, company_id=1, user_agent='mdast_cli/test')


def last_request(rsps):
    return rsps.calls[-1].request


def test_bearer_auth_scheme(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    client.get_architectures()
    assert last_request(mocked_responses).headers['Authorization'] == f'Bearer {TOKEN}'


def test_user_agent_is_sent(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', json=[])
    client.get_architectures()
    assert last_request(mocked_responses).headers['User-Agent'] == 'mdast_cli/test'


def test_engines_url_has_no_organization_segment(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', json=[])
    client.get_engines()
    assert '/organizations/' not in last_request(mocked_responses).url


def test_dedup_url(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/applications/', json=[])
    client.check_app_md5(None, 'a' * 32)
    request = last_request(mocked_responses)
    assert request.url == f'{REST_URL}/applications/?md5={"a" * 32}'
    assert '/organizations/' not in request.url


def test_testcase_url(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/testcases/5/', json={'os': 'ANDROID'})
    client.get_testcase(5)
    assert last_request(mocked_responses).url == f'{REST_URL}/testcases/5/'


def test_create_scan_body_auto(client, mocked_responses):
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/', json={'id': 1}, status=200)
    client.create_auto_scan(project_id=3, profile_id=4, app_md5='b' * 32,
                            arch_id=999, test_case_id=5, os_version='11')
    body = json.loads(last_request(mocked_responses).body)
    assert body == {'md5': 'b' * 32, 'type': 'AUTO', 'testcase_id': 5, 'os_version': '11',
                    'fsm_locked': True, 'project_id': 3, 'profile_id': 4}


def test_create_scan_body_manual_is_manual_type(client, mocked_responses):
    """Scan without a test case is MANUAL (scanyon rejects AUTO without testcase_id);
    testcase_id key stays present (null)."""
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/', json={'id': 1}, status=200)
    client.create_manual_scan(project_id=None, profile_id=None, app_md5='b' * 32)
    body = json.loads(last_request(mocked_responses).body)
    assert body == {'md5': 'b' * 32, 'type': 'MANUAL', 'testcase_id': None, 'fsm_locked': True}
    assert 'architecture_id' not in body
    assert 'application_id' not in body


def test_precheck_body_uses_application_md5_field(client, mocked_responses):
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/start/precheck/',
                         json={'warnings': []})
    client.precheck_scan(
        'c' * 32, profile_id=7, testcase_id=None, scan_type='MANUAL', os_version='11',
    )
    body = json.loads(last_request(mocked_responses).body)
    assert body == {'application_md5': 'c' * 32, 'profile_id': 7,
                    'type': 'MANUAL', 'testcase_id': None, 'os_version': '11'}


def test_scan_lifecycle_urls(client, mocked_responses):
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/start/', json={'id': 77})
    mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/stop/', json={'id': 77})
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/', json={'id': 77})
    client.start_scan(77)
    client.stop_scan(77)
    client.get_scan_info(77)
    urls = [call.request.url for call in mocked_responses.calls]
    assert urls == [f'{REST_URL}/scans/77/start/', f'{REST_URL}/scans/77/stop/',
                    f'{REST_URL}/scans/77/']


def test_report_urls_and_output_param(client, mocked_responses):
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF')
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/report', json={'summary': {}})
    client.download_report(77)
    client.download_scan_json_result(77)
    assert mocked_responses.calls[0].request.url == f'{REST_URL}/scans/77/report?output=pdf'
    assert mocked_responses.calls[1].request.url == f'{REST_URL}/scans/77/report?output=json'


def test_upload_multipart_md5_first_and_headers(client, mocked_responses, tmp_apk, apk_md5):
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/',
                         json={'id': 10}, status=201)
    client.upload_application(tmp_apk)
    request = last_request(mocked_responses)
    body = request.body if isinstance(request.body, bytes) else request.body.read()
    md5_pos = body.index(b'name="md5"')
    file_pos = body.index(b'name="file"')
    assert md5_pos < file_pos, 'md5 multipart field must precede file (facade contract)'
    assert apk_md5.encode() in body
    import os
    assert request.headers['X-File-Size'] == str(os.path.getsize(tmp_apk))
    assert int(request.headers['Content-Length']) >= os.path.getsize(tmp_apk)
    assert 'chunked' not in request.headers.get('Transfer-Encoding', '')


def test_upload_timeout_param(client, mocked_responses, tmp_apk):
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/',
                         json={'id': 10}, status=201)
    client.upload_application(tmp_apk, upload_timeout=120)
    assert 'upload_timeout=120' in last_request(mocked_responses).url


def test_file_md5_is_lower_case_hex(tmp_apk):
    digest = file_md5(tmp_apk)
    assert digest == digest.lower()
    assert len(digest) == 32
    int(digest, 16)


def test_appium_scan_not_supported(client):
    with pytest.raises(NotImplementedError):
        client.create_appium_scan(1, 2, 3, 4, '/tmp/script.py')
