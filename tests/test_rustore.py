import io
import warnings
import zipfile
from unittest import mock

import pytest
from urllib3.exceptions import InsecureRequestWarning

from mdast_cli.distribution_systems import rustore


def _apk_bytes():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('AndroidManifest.xml', b'\x00')
    return buffer.getvalue()


def _rustore_zip_bytes():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('app.apk', _apk_bytes())
    return buffer.getvalue()


def test_download_disables_tls_verification(monkeypatch, tmp_path):
    apk = _rustore_zip_bytes()
    download_url = 'https://static-m.rustore.ru/app.zip'
    monkeypatch.setattr(rustore, 'get_app_info', lambda _package_name: {
        'download_url': download_url,
        'package_name': 'com.example.app',
        'version_name': '1.0',
    })

    response = mock.Mock(
        status_code=200,
        headers={
            'Content-Type': 'application/zip',
            'content-length': str(len(apk)),
        },
    )
    response.iter_content.return_value = [apk]

    def request(*_args, **_kwargs):
        warnings.warn('TLS verification is disabled', InsecureRequestWarning)
        return response

    get = mock.Mock(side_effect=request)
    monkeypatch.setattr(rustore.requests, 'get', get)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = rustore.rustore_download_app('com.example.app', str(tmp_path))

    get.assert_called_once_with(
        download_url,
        headers={
            'User-Agent': 'mdast-cli/1.0 (+https://stingray-tech.ru)',
            'Accept': '*/*',
        },
        stream=True,
        allow_redirects=True,
        timeout=120,
        verify=False,
    )
    assert not caught
    assert zipfile.is_zipfile(result)


def _overall_info_json():
    return {'body': {
        'appId': 42,
        'packageName': 'com.example.app',
        'versionName': '1.0',
        'versionCode': 100,
        'companyName': 'Example LLC',
        'minSdkVersion': 21,
        'maxSdkVersion': 0,
        'targetSdkVersion': 33,
        'fileSize': 1234,
        'iconUrl': 'https://static.rustore.ru/icon.png',
    }}


def _ver_code_stub(statuses_by_ver_code, json_body):
    """Build a requests stub whose status depends on the ruStoreVerCode header sent.

    statuses_by_ver_code maps a ver_code to either a single status or a list of
    statuses returned on successive calls (to emulate RuStore's inconsistent fleet).
    Records every ver_code seen in the returned `seen` list.
    """
    seen = []

    def send(*_args, **kwargs):
        ver_code = kwargs['headers']['ruStoreVerCode']
        seen.append(ver_code)
        status = statuses_by_ver_code.get(ver_code, 419)
        if isinstance(status, list):
            status = status.pop(0) if len(status) > 1 else status[0]
        return mock.Mock(status_code=status, text='',
                         json=mock.Mock(return_value=json_body))

    return mock.Mock(side_effect=send), seen


def test_get_app_info_falls_back_when_ver_code_rejected(monkeypatch):
    """A ver_code outside RuStore's accepted range must not fail the run outright."""
    monkeypatch.setattr(rustore, 'RUSTORE_VER_CODE', '2000000000')
    monkeypatch.setattr(rustore, 'VER_CODE_FALLBACKS', ('247',))

    get, get_seen = _ver_code_stub({'2000000000': 419, '247': 200}, _overall_info_json())
    post, post_seen = _ver_code_stub({'2000000000': 419, '247': 200},
                                     {'body': {'apkUrl': 'https://static.rustore.ru/app.apk'}})
    monkeypatch.setattr(rustore.requests, 'get', get)
    monkeypatch.setattr(rustore.requests, 'post', post)

    info = rustore.get_app_info('com.example.app')

    assert info['download_url'] == 'https://static.rustore.ru/app.apk'
    assert info['package_name'] == 'com.example.app'
    # Rejected value is retried before moving on, then the fallback succeeds.
    assert get_seen == ['2000000000'] * rustore.VER_CODE_ATTEMPTS + ['247']
    assert post_seen == ['2000000000'] * rustore.VER_CODE_ATTEMPTS + ['247']


def test_get_app_info_retries_same_ver_code_on_inconsistent_rejection(monkeypatch):
    """RuStore instances disagree on the accepted range, so a retry alone can succeed."""
    monkeypatch.setattr(rustore, 'RUSTORE_VER_CODE', '1000000')
    monkeypatch.setattr(rustore, 'VER_CODE_FALLBACKS', ('247',))

    get, get_seen = _ver_code_stub({'1000000': [419, 200]}, _overall_info_json())
    post, _ = _ver_code_stub({'1000000': 200},
                             {'body': {'apkUrl': 'https://static.rustore.ru/app.apk'}})
    monkeypatch.setattr(rustore.requests, 'get', get)
    monkeypatch.setattr(rustore.requests, 'post', post)

    info = rustore.get_app_info('com.example.app')

    assert info['version_name'] == '1.0'
    assert get_seen == ['1000000', '1000000']


def test_get_app_info_error_mentions_ver_code_when_all_rejected(monkeypatch):
    monkeypatch.setattr(rustore, 'RUSTORE_VER_CODE', '2000000000')
    monkeypatch.setattr(rustore, 'VER_CODE_FALLBACKS', ('247',))

    get, _ = _ver_code_stub({}, _overall_info_json())
    monkeypatch.setattr(rustore.requests, 'get', get)

    with pytest.raises(RuntimeError) as excinfo:
        rustore.get_app_info('com.example.app')

    assert 'MDAST_RUSTORE_VER_CODE' in str(excinfo.value)
    assert '419' in str(excinfo.value)


def test_default_ver_code_is_inside_accepted_range():
    """Guards against reintroducing a value above RuStore's upper bound (HTTP 419)."""
    assert 247 <= int(rustore.RUSTORE_VER_CODE) <= 1_100_000
