import asyncio
import hashlib
import io
import json
import logging
import subprocess
import shutil
import zipfile
from pathlib import Path

import pytest

from mdast_cli.distribution_systems import google_play_apkeep as gp
from mdast_cli.helpers.apk_artifacts import inspect_apk_artifact
from mdast_cli.helpers import platform_utils


def apk_bytes(abi=None, manifest=True):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as apk:
        if manifest:
            apk.writestr('AndroidManifest.xml', b'test-manifest')
        if abi:
            apk.writestr(f'lib/{abi}/libtest.so', b'ELF-test-library')
    return data.getvalue()


@pytest.mark.parametrize('abi', ['x86_64', 'arm64-v8a', None])
def test_inspect_native_abis(tmp_path, abi):
    artifact = tmp_path / 'app.apk'
    artifact.write_bytes(apk_bytes(abi))
    assert inspect_apk_artifact(artifact) == {'apk_count': 1, 'abis': [abi] if abi else []}


@pytest.mark.parametrize('mode', ['empty', 'missing_manifest', 'broken_apk', 'broken_zip'])
def test_reject_invalid_archives(tmp_path, mode):
    artifact = tmp_path / 'app.zip'
    with zipfile.ZipFile(artifact, 'w') as bundle:
        if mode == 'missing_manifest':
            bundle.writestr('base.apk', apk_bytes(manifest=False))
        elif mode == 'broken_apk':
            bundle.writestr('base.apk', b'not-a-zip')
    if mode == 'broken_zip':
        artifact.write_bytes(b'not-a-zip')
    with pytest.raises(RuntimeError, match='invalid downloaded APK'):
        inspect_apk_artifact(artifact)


def run_download(monkeypatch, tmp_path, replies):
    calls = []
    monkeypatch.setattr(gp, 'get_apkeep_binary_path', lambda: '/verified/apkeep')

    async def create(*args, **kwargs):
        calls.append(args)
        reply = replies[len(calls) - 1]
        work = Path(args[-1])
        if 'abi' in reply:
            split = work / 'com.example.app'
            split.mkdir()
            (split / 'com.example.app.apk').write_bytes(apk_bytes())
            (split / 'split.apk').write_bytes(apk_bytes(reply['abi']))
        if reply.get('empty'):
            (work / 'com.example.app').mkdir()
        if reply.get('bad'):
            (work / 'com.example.app.apk').write_bytes(b'corrupted')

        class Process:
            returncode = reply.get('code', 0)

            async def communicate(self):
                return b'', reply.get('stderr', '').encode()

        return Process()

    monkeypatch.setattr(gp.asyncio, 'create_subprocess_exec', create)
    return calls, lambda: asyncio.run(gp.download_app(str(tmp_path), 'com.example.app', 'user@example.com', 'private-token', 30))


def test_x86_success_without_stdout_marker(monkeypatch, tmp_path, caplog):
    calls, run = run_download(monkeypatch, tmp_path, [{'abi': 'x86_64'}])
    with caplog.at_level(logging.INFO):
        path = run()
    assert inspect_apk_artifact(path)['abis'] == ['x86_64']
    assert len(calls) == 1
    assert 'device=sting_x86_64' in calls[0][calls[0].index('-o') + 1]
    assert 'ARM fallback' not in caplog.text
    assert not list(tmp_path.glob('.google-play-*'))


def test_arm_delivery_is_explicit(monkeypatch, tmp_path, caplog):
    calls, run = run_download(monkeypatch, tmp_path, [{'abi': 'arm64-v8a'}])
    assert inspect_apk_artifact(run())['abis'] == ['arm64-v8a']
    assert 'ARM fallback' in caplog.text
    assert len(calls) == 1


def test_unavailable_x86_retries_arm_once(monkeypatch, tmp_path, caplog):
    calls, run = run_download(monkeypatch, tmp_path, [
        {'code': 3, 'stderr': 'STING_APP_UNAVAILABLE: com.example.app'}, {'abi': 'arm64-v8a'},
    ])
    assert inspect_apk_artifact(run())['abis'] == ['arm64-v8a']
    assert 'device=px_9a' in calls[1][calls[1].index('-o') + 1]
    assert 'ARM fallback' in caplog.text
    assert calls[0][-1] != calls[1][-1]


@pytest.mark.parametrize('reply, error', [
    ({'code': 1, 'stderr': 'Cannot log in private-token user@example.com'}, 'apkeep failed'),
    ({'code': 3, 'stderr': 'network error'}, 'apkeep failed'),
    ({'empty': True}, 'no valid APK artifact'),
    ({'bad': True}, 'no valid APK artifact'),
    ({}, 'no valid APK artifact'),
])
def test_failure_does_not_trigger_fallback(monkeypatch, tmp_path, reply, error):
    calls, run = run_download(monkeypatch, tmp_path, [reply])
    with pytest.raises(RuntimeError, match=error) as raised:
        run()
    assert 'private-token' not in str(raised.value)
    assert 'user@example.com' not in str(raised.value)
    assert len(calls) == 1
    assert not list(tmp_path.glob('.google-play-*'))


def test_old_results_are_not_reused(monkeypatch, tmp_path):
    old = tmp_path / 'com.example.app.apk'
    old.write_bytes(apk_bytes('x86_64'))
    _, run = run_download(monkeypatch, tmp_path, [{}])
    with pytest.raises(RuntimeError, match='no valid APK artifact'):
        run()
    assert old.exists()


def test_bundled_binary_selected_over_path(monkeypatch):
    monkeypatch.setattr(shutil, 'which', lambda _: pytest.fail('PATH must not be used'))
    path = platform_utils.get_apkeep_binary_path()
    assert '/mdast_cli/bin/apkeep-' in path
    assert subprocess.check_output([path, '--version'], text=True).strip() == 'apkeep 1.0.0-sting.3'


def test_corrupt_binary_rejected_before_credentials(monkeypatch):
    class Digest:
        def hexdigest(self): return 'not-the-recorded-hash'
    monkeypatch.setattr(platform_utils.hashlib, 'sha256', lambda _: Digest())
    with pytest.raises(RuntimeError, match='checksum mismatch'):
        platform_utils.get_apkeep_binary_path()
