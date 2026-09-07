"""Protocol boundaries and process cleanup for the native SAP bridge."""
import base64
import io
import json
import subprocess
import time

import pytest
import requests
import responses

from mdast_cli.distribution_systems.appstore_client import sap
from mdast_cli.distribution_systems.appstore_client.store import StoreClient

BAG = {
    'authenticateAccount': 'https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate',
    'sign-sap-setup': 'https://fpinit.itunes.apple.com/v1/signSapSetup/legacy',
    'sign-sap-setup-cert': 'https://s.mzstatic.com/sap/setupCert.plist',
    'sign-sap-version': '200',
}


@pytest.mark.parametrize('wrapper', [lambda x:x, lambda x:{'urlBag':x}, lambda x:{'URLBag':x}])
def test_bag_accepts_apple_certificate_cdn(wrapper):
    assert sap.parse_bag(wrapper(BAG))['certificate_url'] == BAG['sign-sap-setup-cert']


@pytest.mark.parametrize('field,value', [
    ('sign-sap-version', None), ('sign-sap-version', '201'),
    ('authenticateAccount', 'https://evil.example/'),
    ('sign-sap-setup', 'http://fpinit.itunes.apple.com/setup'),
    ('sign-sap-setup-cert', 'https://s.mzstatic.com.evil.example/setupCert.plist'),
    ('sign-sap-setup-cert', None),
])
def test_bag_fails_closed_on_invalid_configuration(field, value):
    with pytest.raises(sap.SAPError):
        sap.parse_bag(dict(BAG, **{field:value}))


@responses.activate
def test_bag_uses_configurator_user_agent_and_requires_sap():
    import plistlib
    url = 'https://init.itunes.apple.com/bag.xml?guid=AABBCCDDEEFF'
    responses.get(url, body=plistlib.dumps({'urlBag': BAG}), status=200)
    client = StoreClient(requests.Session(), guid='AABBCCDDEEFF')
    assert client.get_bag()['version'] == 200
    assert responses.calls[0].request.headers['User-Agent'].startswith('Configurator/')


class Process:
    def __init__(self, output):
        self.stdin, self.stdout = io.BytesIO(), io.BytesIO(output)
        self.returncode = None
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = -15

    def wait(self, timeout=None):
        return self.returncode


def make_signer(monkeypatch, output):
    process = Process(output)
    monkeypatch.setattr(sap, 'helper_command', lambda: ['/test/mdast-sap'])
    captured = {}
    def popen(args, **kwargs):
        captured.update(args=args, **kwargs)
        return process
    monkeypatch.setattr(sap.subprocess, 'Popen', popen)
    return process, captured


def test_protocol_keeps_credentials_out_of_process_arguments(monkeypatch):
    process, captured = make_signer(monkeypatch, b'{"ok":true}\n{"ok":true,"signature":"YWJj"}\n')
    with sap.SAPSigner(sap.parse_bag(BAG), 'AABBCCDDEEFF') as signer:
        assert signer.sign(b'private request bytes') == base64.b64encode(b'abc').decode()
        sent = [json.loads(line) for line in process.stdin.getvalue().splitlines()]
        assert base64.b64decode(sent[1]['payload']) == b'private request bytes'
    assert captured['args'] == ['/test/mdast-sap']
    assert captured['stderr'] == subprocess.DEVNULL
    assert process.terminated


@pytest.mark.parametrize('output', [b'', b'no json\n', b'[]\n', b'{}\n', b'{"ok":false,"detail":"private"}\n', b'x'*(sap.MAX_MESSAGE+1)])
def test_invalid_init_response_reaps_helper_without_leaking_output(monkeypatch, output):
    process, _ = make_signer(monkeypatch, output)
    with pytest.raises(sap.SAPError) as error:
        sap.SAPSigner(sap.parse_bag(BAG), 'AABBCCDDEEFF')
    assert 'private' not in str(error.value)
    assert process.terminated


def test_setup_timeout_reaps_helper(monkeypatch):
    process, _ = make_signer(monkeypatch, b'')
    class SlowOutput(io.BytesIO):
        def readline(self, *_):
            time.sleep(0.03)
            return b''
    process.stdout = SlowOutput()
    monkeypatch.setattr(sap, 'SETUP_TIMEOUT', 0.001)
    with pytest.raises(sap.SAPError, match='timed out'):
        sap.SAPSigner(sap.parse_bag(BAG), 'AABBCCDDEEFF')
    assert process.terminated


@pytest.mark.parametrize('signature', [None, '', '@@@', ' '])
def test_invalid_signature_rejected(monkeypatch, signature):
    output = b'{"ok":true}\n' + json.dumps({'ok':True, 'signature':signature}).encode()+b'\n'
    process, _ = make_signer(monkeypatch, output)
    with sap.SAPSigner(sap.parse_bag(BAG), 'AABBCCDDEEFF') as signer:
        with pytest.raises(sap.SAPError, match='signature'):
            signer.sign(b'private')
    assert process.terminated


def test_compiled_helper_protocol_without_network():
    try:
        binary = sap.helper_path()
    except sap.SAPError:
        pytest.skip('helper not built in this source checkout')
    result = subprocess.run([str(binary)], input=b'{"op":"sign","payload":"YWJj"}\n',
                            capture_output=True, timeout=10)
    assert result.returncode == 0
    assert json.loads(result.stdout)['error'] == 'invalid_sign_state'
    assert b'YWJj' not in result.stderr


@pytest.mark.parametrize('machine,loader', [('x86_64','/lib/ld-musl-x86_64.so.1'), ('aarch64','/lib/ld-musl-aarch64.so.1')])
def test_musl_uses_system_loader(monkeypatch, machine, loader):
    monkeypatch.setattr(sap, 'helper_path', lambda: '/test/mdast-sap')
    monkeypatch.setattr(sap.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(sap.platform, 'machine', lambda: machine)
    monkeypatch.setattr(sap.Path, 'is_file', lambda self: str(self) == loader)
    assert sap.helper_command() == [loader, '/test/mdast-sap']
