"""Positive e2e: download a build from a store, then scan it in Sting (microservices).

Each test mocks the store's HTTP endpoints to deliver a valid APK, then lets the
CLI run the full microservices flow (upload -> precheck -> create -> start -> poll
-> report) against the mocked Sting facade. This is the happy path of the
"download from store -> scan" integration, one store per test.

Store-side FAILURE modes are intentionally NOT here (per scope: negatives cover
work with Sting, positives cover download-from-store + scan). See test_negative_e2e.py.
"""
import hashlib
import io
import json
import os
import zipfile

import pytest
import responses
from responses import matchers

from tests.conftest import (BASE_URL, REST_URL, TOKEN, application_json, run_main,
                            scan_json)
from tests.test_smoke_flows import register_ms_happy_path

pytestmark = pytest.mark.e2e

APK_BYTES = b'PK\x03\x04' + b'fake-apk-payload' * 64


def _valid_zip_apk():
    """A real (minimal) zip — APK is a zip; some downloaders (rustore) validate the container."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('AndroidManifest.xml', b'\x00')
    return buf.getvalue()


APK_ZIP = _valid_zip_apk()


def _write_app(download_path, name):
    """Write a real app file to download_path and return its path (for monkeypatched downloaders)."""
    os.makedirs(str(download_path), exist_ok=True)
    p = os.path.join(str(download_path), name)
    with open(p, 'wb') as f:
        f.write(APK_ZIP)
    return p


def scan_argv(distribution_argv, download_path):
    """Common scan flags appended to a store's download flags."""
    return distribution_argv + [
        '--download_path', str(download_path),
        '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
        '--profile_id', '2', '--testcase_id', '5', '--report_format', 'json',
    ]


def _assert_scanned_ok(exit_code, mocked_responses):
    assert exit_code == 0
    # the scan was actually created against the facade with the downloaded build
    creates = [c for c in mocked_responses.calls if c.request.url == f'{REST_URL}/scans/start/']
    assert creates, 'a scan must be created from the downloaded store build'


# --- RuMarket ---------------------------------------------------------------

def test_rumarket_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5,
                                     no_sleep, ms_mode):
    # store: app info + apk download
    mocked_responses.add(responses.GET,
                         'https://store-api.ruplay.market/api/v1/app/getApp/com.example.app',
                         json={'data': {
                             'packageName': 'com.example.app',
                             'author': {'name': 'Acme'},
                             'iconUrl': 'https://x/icon.png',
                             'latestApk': {'name': 'app.apk', 'versionName': '1.0',
                                           'versionCode': 1, 'minSdkVersion': 21,
                                           'targetSdkVersion': 33, 'size': len(APK_BYTES)},
                         }})
    mocked_responses.add(responses.GET, 'https://cdn.ruplay.market/data/apks/app.apk',
                         body=APK_BYTES, content_type='application/vnd.android.package-archive')
    # Sting happy path
    register_ms_happy_path(mocked_responses, apk_md5)
    exit_code = run_main(monkeypatch, scan_argv(
        ['--distribution_system', 'rumarket', '--rumarket_package_name', 'com.example.app'],
        tmp_path))
    _assert_scanned_ok(exit_code, mocked_responses)


# --- Huawei AppGallery ------------------------------------------------------

def test_appgallery_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5,
                                       no_sleep, ms_mode):
    mocked_responses.add(responses.POST,
                         'https://web-drru.hispace.dbankcloud.ru/webedge/getInterfaceCode',
                         json='ifc-code')
    mocked_responses.add(responses.GET,
                         'https://web-drru.hispace.dbankcloud.ru/uowap/index',
                         json={'layoutData': [{'dataList': [{
                             'package': 'com.example.app', 'appid': 'C123', 'name': 'App',
                             'versionName': '1.0', 'versionCode': 1, 'targetSDK': 33,
                             'size': len(APK_BYTES), 'md5': 'abc', 'icon': 'https://x/i.png'}]}]})
    mocked_responses.add(responses.GET,
                         'https://appgallery.cloud.huawei.com/appdl/C123',
                         body=APK_BYTES, content_type='application/vnd.android.package-archive')
    register_ms_happy_path(mocked_responses, apk_md5)
    exit_code = run_main(monkeypatch, scan_argv(
        ['--distribution_system', 'appgallery', '--appgallery_app_id', 'C123'],
        tmp_path))
    _assert_scanned_ok(exit_code, mocked_responses)


# --- Nexus 3 (session + search + download) ---
def test_nexus_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    nx = 'http://nexus.example'
    mocked_responses.add(responses.POST, f'{nx}/service/rapture/session', json={}, status=200)
    mocked_responses.add(responses.GET, f'{nx}/service/rest/v1/search', json={'items': [{'assets': [{
        'contentType': 'application/vnd.android.package-archive', 'downloadUrl': f'{nx}/repo/app.apk'}]}]})
    mocked_responses.add(responses.GET, f'{nx}/repo/app.apk', body=APK_BYTES)
    register_ms_happy_path(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'nexus', '--nexus_url', nx, '--nexus_login', 'u',
            '--nexus_password', 'p', '--nexus_repo_name', 'releases', '--nexus_group_id', 'com.example',
            '--nexus_artifact_id', 'app', '--nexus_version', '1.0']
    _assert_scanned_ok(run_main(monkeypatch, scan_argv(argv, tmp_path)), mocked_responses)


# --- Nexus 2 (maven content GET) ---
def test_nexus2_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    nx = 'http://nexus2.example'
    mocked_responses.add(responses.GET, f'{nx}/service/local/artifact/maven/content', body=APK_BYTES)
    register_ms_happy_path(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'nexus2', '--nexus2_url', nx, '--nexus2_login', 'u',
            '--nexus2_password', 'p', '--nexus2_repo_name', 'releases', '--nexus2_group_id', 'com.example',
            '--nexus2_artifact_id', 'app', '--nexus2_version', '1.0', '--nexus2_extension', 'apk']
    _assert_scanned_ok(run_main(monkeypatch, scan_argv(argv, tmp_path)), mocked_responses)


# --- RuStore (overallInfo + download-link + apk; validates zip container) ---
def test_rustore_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    mocked_responses.add(responses.GET,
        'https://backapi.rustore.ru/applicationData/overallInfo/com.example.app',
        json={'body': {'appId': 42, 'packageName': 'com.example.app', 'versionName': '1.0',
                       'versionCode': 1, 'minSdkVersion': 21, 'maxSdkVersion': 33, 'targetSdkVersion': 33,
                       'fileSize': len(APK_ZIP), 'iconUrl': 'https://x/i.png', 'companyName': 'Acme'}})
    mocked_responses.add(responses.POST, 'https://backapi.rustore.ru/applicationData/download-link',
        json={'body': {'apkUrl': 'https://cdn.rustore.example/app.apk'}})
    mocked_responses.add(responses.GET, 'https://cdn.rustore.example/app.apk', body=APK_ZIP,
        content_type='application/vnd.android.package-archive')
    register_ms_happy_path(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'rustore', '--rustore_package_name', 'com.example.app']
    _assert_scanned_ok(run_main(monkeypatch, scan_argv(argv, tmp_path)), mocked_responses)


# --- Firebase (downloader monkeypatched: google-auth/service-account internals out of scope) ---
def test_firebase_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    monkeypatch.setattr('mdast_cli.mdast_scan.firebase_download_app',
                        lambda download_path, *a, **k: _write_app(download_path, 'fb_app-1.0.apk'))
    register_ms_happy_path(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'firebase', '--firebase_project_number', '123',
            '--firebase_app_id', '1:123:android:abc', '--firebase_account_json_path', '/tmp/fake.json',
            '--firebase_file_extension', 'apk']
    _assert_scanned_ok(run_main(monkeypatch, scan_argv(argv, tmp_path)), mocked_responses)


# --- Google Play (apkeep subprocess monkeypatched) ---
def test_google_play_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    monkeypatch.setattr('mdast_cli.mdast_scan.GooglePlay.login', lambda self: None)
    monkeypatch.setattr('mdast_cli.mdast_scan.GooglePlay.download_app',
                        lambda self, download_path, *a, **k: _write_app(download_path, 'gp_app-1.0.apk'))
    register_ms_happy_path(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'google_play', '--google_play_package_name', 'com.example.app',
            '--google_play_email', 'u@example.com', '--google_play_aas_token', 'aas_et/xxx']
    _assert_scanned_ok(run_main(monkeypatch, scan_argv(argv, tmp_path)), mocked_responses)


# --- Apple App Store (iOS; StoreClient monkeypatched). iOS -> manual scan on an iOS engine. ---
def _register_ms_ios_manual(rsps, apk_md5):
    rsps.add(responses.GET, f'{REST_URL}/architectures/',
             json=[{'id': 3, 'type': 'IOS', 'os_version': '16', 'name': 'iOS 16'}])
    rsps.add(responses.GET, f'{REST_URL}/engines/', json=[{'type': 'IOS', 'status': 'STARTED'}])
    rsps.add(responses.GET, f'{REST_URL}/applications/', json=[])
    rsps.add(responses.POST, f'{REST_URL}/applications/upload_info/',
             json=application_json(apk_md5), status=201)
    rsps.add(responses.POST, f'{REST_URL}/scans/start/precheck/', json={'warnings': []})
    rsps.add(responses.POST, f'{REST_URL}/scans/start/',
             json=scan_json(stage='CREATED', status='INITIAL', type='MANUAL'))
    rsps.add(responses.POST, f'{REST_URL}/scans/77/start/',
             json=scan_json(stage='WORKING', status='PROCESSING'))
    rsps.add(responses.POST, f'{REST_URL}/scans/77/stop/',
             json=scan_json(stage='STOP', status='PROCESSING'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/', json=scan_json(stage='WORKING', status='PROCESSING'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/', json=scan_json(stage='SUCCESS', status='COMPLETE'))
    rsps.add(responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 x',
             match=[matchers.query_param_matcher({'output': 'pdf'})])


def test_appstore_download_then_scan(mocked_responses, monkeypatch, tmp_path, apk_md5, no_sleep, ms_mode):
    # The AppStore downloader returns its own md5 ('d'*32) as the 2nd tuple element.
    # F1: on the microservices installation that md5 is DELIBERATELY ignored - the
    # Apple store md5 differs from the file actually uploaded (post-download the IPA
    # is re-signed/re-zipped), so dedup/precheck/create must key off the LOCAL file md5.
    appstore_md5 = 'd' * 32
    monkeypatch.setattr('mdast_cli.mdast_scan.AppStore.download_app',
                        lambda self, download_path, *a, **k: (_write_app(download_path, 'as_app-1.0.ipa'), appstore_md5))
    _register_ms_ios_manual(mocked_responses, apk_md5)
    argv = ['--distribution_system', 'appstore', '--appstore_app_id', '123',
            '--appstore_apple_id', 'u@example.com', '--appstore_password', 'pw', '--appstore_2FA', '123456',
            '--download_path', str(tmp_path), '--url', BASE_URL, '--company_id', '1', '--token', TOKEN,
            '--profile_id', '2']
    _assert_scanned_ok(run_main(monkeypatch, argv), mocked_responses)

    # The local file md5 (of what was actually written/uploaded), NOT the Apple md5.
    local_md5 = hashlib.md5(APK_ZIP).hexdigest().lower()
    assert local_md5 != appstore_md5
    # create-scan (POST /scans/start/) must carry the local file md5, not 'd'*32.
    create = next(c for c in mocked_responses.calls
                  if c.request.url == f'{REST_URL}/scans/start/' and c.request.method == 'POST')
    assert json.loads(create.request.body)['md5'] == local_md5
    # ...and the Apple store md5 must appear nowhere in the create/precheck payloads.
    for c in mocked_responses.calls:
        if c.request.method == 'POST' and c.request.body and isinstance(c.request.body, (str, bytes)):
            body = c.request.body if isinstance(c.request.body, str) else c.request.body.decode('utf-8', 'ignore')
            assert appstore_md5 not in body
