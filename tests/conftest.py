import hashlib
import sys

import pytest
import responses as responses_lib

BASE_URL = 'https://stand.example'
REST_URL = f'{BASE_URL}/rest'
TOKEN = 'very-secret-org-token-value-1234567890'
COMPANY_ID = '1'


@pytest.fixture
def tmp_apk(tmp_path):
    path = tmp_path / 'app.apk'
    path.write_bytes(b'PK\x03\x04' + b'binary-payload' * 128)
    return str(path)


@pytest.fixture
def apk_md5(tmp_apk):
    with open(tmp_apk, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest().lower()


@pytest.fixture
def mocked_responses():
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda *_args, **_kwargs: None)


@pytest.fixture
def ms_mode(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'microservices')


@pytest.fixture
def monolith_mode(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'monolith')


def run_main(monkeypatch, argv):
    """Run mdast_scan.main() with the given CLI args, return the exit code.

    The monolith success path returns from main() without sys.exit - that is
    process exit code 0.
    """
    from mdast_cli import mdast_scan
    monkeypatch.setattr(sys, 'argv', ['mdast_cli'] + argv)
    try:
        mdast_scan.main()
    except SystemExit as excinfo:
        return int(excinfo.code or 0)
    return 0


def scan_json(scan_id=77, stage='WORKING', status='PROCESSING', message=None, **extra):
    payload = {
        'id': scan_id,
        'stage': stage,
        'status': status,
        'message': message,
        'md5': 'a' * 32,
        'type': 'AUTO',
        'testcase_id': None,
        'storage_id': None,
        'project': {'id': 1, 'name': 'proj'},
        'profile': {'id': 2, 'name': 'prof'},
        'fsm_locked': False,
    }
    payload.update(extra)
    return payload


def application_json(md5, app_id=10):
    return {
        'id': app_id,
        'architecture_type': 'Android',
        'file_url': 'https://s3.example/presigned',
        'icon_url': None,
        'name': 'Example App',
        'package_name': 'com.example.app',
        'md5': md5,
        'file_size': 1234,
        'version_code': 1,
        'version_name': '1.0',
        'min_sdk_version': '21',
        'max_sdk_version': None,
        'target_sdk_version': '33',
        'main_activity': 'com.example.Main',
        'main_activities_objects': [],
        'is_debuggable': False,
        'signature': 'abc',
        'is_parked': False,
        'distribution_type': 0,
    }
