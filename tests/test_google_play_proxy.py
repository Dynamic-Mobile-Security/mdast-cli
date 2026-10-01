import asyncio
import os
import socket
import threading
from pathlib import Path

import pytest

from mdast_cli.distribution_systems import google_play_apkeep as gp
from mdast_cli.distribution_systems.google_play import GooglePlay
from test_google_play_artifacts import apk_bytes

PROXY = 'socks5h://proxy-user:secret%40word@127.0.0.1:1080'


@pytest.mark.parametrize('proxy', [None, PROXY, 'http://localhost:3128', 'https://localhost:3128', 'socks5://localhost:1080'])
def test_route_is_child_scoped_and_overrides_ambient_environment(monkeypatch, proxy):
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.setenv(name, 'http://ambient.invalid:1234')
    monkeypatch.setenv('NO_PROXY', '*')
    before = os.environ.copy()
    env = gp._proxy_environment(proxy)
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        assert env[name] == (proxy or '')
    assert env['NO_PROXY'] == env['no_proxy'] == ('' if proxy else '*')
    assert dict(os.environ) == before


@pytest.mark.parametrize('proxy', ['', '127.0.0.1:1080', 'ftp://host', 'socks5://',
                                   'http://host:bad', 'http://host:0', 'http://host:65536',
                                   'http://host/path', 'http://host?query', 'http://host#fragment',
                                   'http://private-password@host\n'])
def test_invalid_proxy_rejected_without_echoing_input(monkeypatch, tmp_path, proxy):
    monkeypatch.setattr(gp, 'get_apkeep_binary_path', lambda: pytest.fail('must validate before binary'))
    with pytest.raises(ValueError, match='invalid proxy URL') as error:
        asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'email', 'token', 30, proxy))
    assert 'private-password' not in str(error.value)


def fake_process(monkeypatch, replies):
    calls = []
    monkeypatch.setattr(gp, 'get_apkeep_binary_path', lambda: '/verified/apkeep')

    async def create(*args, **kwargs):
        reply = replies[len(calls)]
        calls.append((args, kwargs))
        if '-a' in args:
            directory = Path(args[-1])
            assert not any(directory.iterdir())
            if reply.get('partial'):
                split = directory / 'com.example.app'
                split.mkdir()
                (split / 'partial.apk').write_bytes(b'incomplete')
            if reply.get('artifact'):
                (directory / 'com.example.app.apk').write_bytes(apk_bytes('x86_64'))

        class Process:
            returncode = reply.get('code', 0)

            async def communicate(self):
                return reply.get('stdout', '').encode(), reply.get('stderr', '').encode()

        return Process()

    monkeypatch.setattr(gp.asyncio, 'create_subprocess_exec', create)
    return calls


@pytest.mark.parametrize('proxy', [None, PROXY])
def test_public_python_api_passes_route(monkeypatch, tmp_path, proxy):
    calls = fake_process(monkeypatch, [{'artifact': True}])
    GooglePlay('user@example.com', 'private-token').download_app(str(tmp_path), 'com.example.app', proxy=proxy)
    args, kwargs = calls[0]
    assert kwargs['env']['HTTPS_PROXY'] == (proxy or '')
    assert not any('proxy-user' in arg for arg in args)


@pytest.mark.parametrize('proxy', [None, PROXY])
def test_oauth_and_download_receive_same_route(monkeypatch, tmp_path, proxy):
    calls = fake_process(monkeypatch, [{'stdout': 'AAS Token: aas-secret'}, {'artifact': True}])
    monkeypatch.setattr(gp, 'DEFAULT_DOWNLOAD_DIR', str(tmp_path))
    assert asyncio.run(gp._run_cli('user@example.com', 'com.example.app', 'oauth-secret', None, proxy)) == 0
    assert len(calls) == 2
    for _, kwargs in calls:
        assert kwargs['env']['HTTPS_PROXY'] == (proxy or '')
        assert kwargs['env']['NO_PROXY'] == ('' if proxy else '*')


def test_partial_failure_retries_fresh_directory(monkeypatch, tmp_path):
    calls = fake_process(monkeypatch, [
        {'partial': True, 'code': 3, 'stderr': 'STING_DOWNLOAD_ERROR: timed out'}, {'artifact': True},
    ])
    old = tmp_path / 'unrelated.apk'
    old.write_bytes(b'keep me')
    artifact = asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'email', 'token', 30, PROXY))
    assert Path(artifact).is_file()
    assert old.read_bytes() == b'keep me'
    assert len({args[-1] for args, _ in calls}) == 2
    assert all(not Path(args[-1]).exists() for args, _ in calls)
    assert all(kwargs['env']['HTTPS_PROXY'] == PROXY for _, kwargs in calls)
    assert all('device=sting_x86_64' in args[args.index('-o') + 1] for args, _ in calls)


def test_retries_exhaust_without_direct_or_arm_fallback_and_hide_secrets(monkeypatch, tmp_path):
    message = f'STING_DOWNLOAD_ERROR: {PROXY} proxy-user secret@word secret%40word private-token user@example.com'
    calls = fake_process(monkeypatch, [{'partial': True, 'code': 3, 'stderr': message}] * 3)
    with pytest.raises(RuntimeError, match='through configured proxy') as error:
        asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'user@example.com', 'private-token', 30, PROXY))
    assert len(calls) == 3
    assert all(kwargs['env']['HTTPS_PROXY'] == PROXY for _, kwargs in calls)
    assert all('device=sting_x86_64' in args[args.index('-o') + 1] for args, _ in calls)
    for secret in ('proxy-user', 'secret@word', 'secret%40word', 'private-token', 'user@example.com'):
        assert secret not in str(error.value)
    assert not list(tmp_path.glob('.google-play-*'))


def test_oauth_hides_proxy_secrets(monkeypatch, caplog):
    fake_process(monkeypatch, [{'code': 1, 'stderr': f'{PROXY} proxy-user secret@word oauth-secret'}])
    with pytest.raises(RuntimeError) as error:
        asyncio.run(gp.fetch_aas_token('user@example.com', 'oauth-secret', 30, PROXY))
    for secret in ('proxy-user', 'secret@word', 'oauth-secret'):
        assert secret not in str(error.value) + caplog.text


def test_existing_cli_flag_reaches_oauth_and_download(monkeypatch, tmp_path):
    from conftest import run_main
    calls = fake_process(monkeypatch, [{'stdout': 'AAS Token: aas-secret'}, {'artifact': True}])
    result = run_main(monkeypatch, ['--download_only', '--distribution_system', 'google_play',
                      '--google_play_package_name', 'com.example.app', '--google_play_email', 'user@example.com',
                      '--google_play_oauth2_token', 'oauth-secret', '--google_play_proxy', PROXY,
                      '--download_path', str(tmp_path)])
    assert result == 0
    assert len(calls) == 2
    assert all(kwargs['env']['HTTPS_PROXY'] == PROXY for _, kwargs in calls)


def test_timeout_terminates_child_and_does_not_retry(monkeypatch, tmp_path):
    state = {'killed': False, 'waited': False, 'calls': 0}
    monkeypatch.setattr(gp, 'get_apkeep_binary_path', lambda: '/verified/apkeep')

    class Process:
        returncode = None

        async def communicate(self):
            await asyncio.sleep(10)

        def kill(self):
            state['killed'] = True

        async def wait(self):
            state['waited'] = True

    async def create(*args, **kwargs):
        state['calls'] += 1
        return Process()

    monkeypatch.setattr(gp.asyncio, 'create_subprocess_exec', create)
    with pytest.raises(RuntimeError, match='timeout'):
        asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'email', 'token', 0.01, PROXY))
    assert state == {'killed': True, 'waited': True, 'calls': 1}
    assert not list(tmp_path.glob('.google-play-*'))


def test_bundled_apkeep_speaks_authenticated_socks(monkeypatch):
    """Real bundled binary, local server, dummy credentials; no Google traffic."""
    events = []
    errors = []
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen()
    listener.settimeout(10)

    def read_exact(conn, count):
        result = b''
        while len(result) < count:
            part = conn.recv(count - len(result))
            if not part:
                raise EOFError
            result += part
        return result

    def serve():
        try:
            conn, _ = listener.accept()
            with conn:
                conn.settimeout(5)
                version, count = read_exact(conn, 2)
                methods = read_exact(conn, count)
                events.append(('greeting', version, 2 in methods))
                conn.sendall(b'\x05\x02')
                version, count = read_exact(conn, 2)
                user = read_exact(conn, count)
                password = read_exact(conn, read_exact(conn, 1)[0])
                events.append(('auth', version, user, password))
                conn.sendall(b'\x01\x01')  # reject; must never contact Google directly
        except Exception as exc:
            errors.append(type(exc).__name__)
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    proxy = f'socks5h://test-user:test-pass@127.0.0.1:{listener.getsockname()[1]}'
    with pytest.raises(RuntimeError):
        asyncio.run(gp.fetch_aas_token('test@example.com', 'dummy-token', 8, proxy))
    thread.join(11)
    assert not errors
    assert events == [('greeting', 5, True), ('auth', 1, b'test-user', b'test-pass')]


def test_retry_budget_is_shared(monkeypatch, tmp_path):
    calls = []
    killed = []
    monkeypatch.setattr(gp, 'get_apkeep_binary_path', lambda: '/verified/apkeep')

    class Process:
        returncode = None

        async def communicate(self):
            await asyncio.sleep(0.04)
            self.returncode = 3
            return b'', b'STING_DOWNLOAD_ERROR: timeout'

        def kill(self):
            killed.append(True)

        async def wait(self):
            return -9

    async def create(*args, **kwargs):
        calls.append(args)
        return Process()

    monkeypatch.setattr(gp.asyncio, 'create_subprocess_exec', create)
    with pytest.raises(RuntimeError, match='timeout'):
        asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'email', 'token', 0.06))
    assert 1 <= len(calls) <= 2
    assert killed == [True]
    assert not list(tmp_path.glob('.google-play-*'))
