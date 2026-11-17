import asyncio

import pytest

from mdast_cli.distribution_systems import google_play_apkeep as gp
from tests.test_google_play_artifacts import run_download


@pytest.mark.parametrize('message,expected', [
    ('STING_DOWNLOAD_ERROR: Status(503, None)', True),
    ('STING_DOWNLOAD_ERROR: Status(429, None)', True),
    ('HTTP 408 Request Timeout', True),
    ('HTTP/1.1 502 Bad Gateway', True),
    ('STING_DOWNLOAD_ERROR: connection reset by peer', True),
    ('Could not log in. Please check your credentials. error sending request for url', True),
    ('error sending request: certificate verify failed', False),
    ('STING_DOWNLOAD_ERROR: timed out', True),
    ('STING_DOWNLOAD_ERROR: Status(403, None)', False),
    ('STING_DOWNLOAD_ERROR: Status(401, None)', False),
    ('STING_DOWNLOAD_ERROR: Status(404, None)', False),
    ('Could not log in. Invalid payload.', False),
    ('STING_DOWNLOAD_ERROR: unexpected response', False),
    ('STING_APP_UNAVAILABLE: com.example.app', False),
])
def test_error_classification(message, expected):
    assert gp._is_temporary_error(message) is expected


@pytest.mark.parametrize('succeed', [False, True])
def test_503_backoff_budget(monkeypatch, tmp_path, succeed):
    error = {'code': 3, 'stderr': 'STING_DOWNLOAD_ERROR: Status(503, None)'}
    replies = [error, {'abi': 'x86_64'}] if succeed else [error] * 3
    calls, run = run_download(monkeypatch, tmp_path, replies)
    sleeps = []

    async def sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr(gp.asyncio, 'sleep', sleep)
    if succeed:
        assert run().endswith(('.apk', '.zip', '.apks'))
        assert sleeps == [2]
    else:
        with pytest.raises(gp.GooglePlayTemporaryError):
            run()
        assert sleeps == [2, 5]
    assert len(calls) == len(replies)
    assert all('device=sting_x86_64' in c[c.index('-o') + 1] for c in calls)
    assert not list(tmp_path.glob('.google-play-*'))


@pytest.mark.parametrize('code', [401, 403, 404])
def test_permanent_failure_has_no_retry(monkeypatch, tmp_path, code):
    calls, run = run_download(monkeypatch, tmp_path, [
        {'code': 3, 'stderr': f'STING_DOWNLOAD_ERROR: Status({code}, None)'},
    ])
    with pytest.raises(RuntimeError) as raised:
        run()
    assert not isinstance(raised.value, gp.GooglePlayTemporaryError)
    assert len(calls) == 1
