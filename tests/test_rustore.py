import io
import warnings
import zipfile
from unittest import mock

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
