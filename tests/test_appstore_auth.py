"""Signed App Store authentication and existing download regressions."""
import base64
import plistlib

import pytest
import requests

from mdast_cli.distribution_systems.appstore_client import store as store_mod
from mdast_cli.distribution_systems.appstore_client.store import LEGACY_AUTH_URL, StoreClient, StoreException

POD_URL = "https://p7-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?Pod=7&PRH=7"
SUCCESS_PLIST = {
    "m-allowed": True, "passwordToken": "token-123", "download-queue-info": {"dsid": 4242},
    "accountInfo": {"address": {"firstName": "Test", "lastName": "User"}},
}
BAG_CONFIG = {
    'auth_url': LEGACY_AUTH_URL, 'setup_url': 'https://fpinit.itunes.apple.com/setup',
    'certificate_url': 'https://s.mzstatic.com/sap/setupCert.plist', 'version': 200,
}


class FakeResponse:
    def __init__(self, status_code, content=b"", headers=None, url=""):
        self.status_code, self.content = status_code, content
        self.headers, self.url = headers or {}, url


class FakeSession:
    def __init__(self, responses):
        self._responses, self.headers, self.calls = list(responses), {}, []

    def mount(self, *args):
        pass

    def post(self, url, headers=None, data=None, **kwargs):
        self.calls.append({'url': url, 'body': plistlib.loads(data), 'data': data, 'headers': headers, **kwargs})
        return self._responses.pop(0)


class FakeSigner:
    def __init__(self, config, guid):
        self.payloads, self.closed = [], False
        FakeSigner.last = self

    def sign(self, payload):
        self.payloads.append(payload)
        return base64.b64encode(b'signed:' + payload).decode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True


def _client(responses):
    return StoreClient(FakeSession(responses), guid='12367150C7F5')


@pytest.fixture(autouse=True)
def _signed_bag(monkeypatch):
    monkeypatch.setattr(store_mod.time, 'sleep', lambda *_: None)
    monkeypatch.setattr(StoreClient, 'get_bag', lambda self: BAG_CONFIG)
    monkeypatch.setattr(store_mod, 'SAPSigner', FakeSigner)


def test_pod_redirect_reposts_body_with_attempt_one():
    client = _client([
        FakeResponse(302, headers={'Location': POD_URL}),
        FakeResponse(200, plistlib.dumps(SUCCESS_PLIST), headers={'pod': '7'}, url=POD_URL),
    ])
    response = client.authenticate('user@example.com', 'secret123456')
    assert response.passwordToken == 'token-123'
    assert client.account_name == 'Test User'
    assert client.pod == '7'
    assert [c['url'] for c in client.sess.calls] == [LEGACY_AUTH_URL, POD_URL]
    assert [c['body']['attempt'] for c in client.sess.calls] == ['1', '1']
    assert FakeSigner.last.payloads == [c['data'] for c in client.sess.calls]
    assert len(set(FakeSigner.last.payloads)) == 1
    assert FakeSigner.last.closed


@pytest.mark.parametrize('status', [204, 404, 500, 503, 504])
def test_transient_response_retries_same_signed_endpoint(status):
    client = _client([FakeResponse(status), FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret123456')
    assert [c['url'] for c in client.sess.calls] == [LEGACY_AUTH_URL] * 2
    assert len(set(FakeSigner.last.payloads)) == 1
    assert len(FakeSigner.last.payloads) == 2


def test_invalid_credentials_are_reported():
    failure = {'failureType': '1234', 'customerMessage': 'Incorrect password'}
    client = _client([FakeResponse(200, plistlib.dumps(failure))])
    with pytest.raises(StoreException, match='Incorrect password'):
        client.authenticate('user@example.com', 'wrong')
    assert len(client.sess.calls) == 1
    assert FakeSigner.last.closed


def test_first_attempt_invalid_credentials_retried_once():
    failure = {'failureType': '-5000', 'customerMessage': 'retry'}
    client = _client([FakeResponse(200, plistlib.dumps(failure)), FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret')
    assert [c['body']['attempt'] for c in client.sess.calls] == ['1', '2']
    assert FakeSigner.last.payloads[0] != FakeSigner.last.payloads[1]


def test_forbidden_response_fails_without_unsigned_fallback():
    client = _client([FakeResponse(403)])
    with pytest.raises(StoreException, match='HTTP 403'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1
    assert FakeSigner.last.closed


def test_transient_response_budget_is_three():
    client = _client([FakeResponse(204) for _ in range(3)])
    with pytest.raises(StoreException, match='HTTP 204'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 3


def test_html_forbidden_is_retried_with_backoff(monkeypatch):
    waits = []
    monkeypatch.setattr(store_mod.time, 'sleep', waits.append)
    client = _client([
        FakeResponse(403, b'<html>Forbidden</html>', {'Content-Type': 'text/html'}),
        FakeResponse(404), FakeResponse(200, plistlib.dumps(SUCCESS_PLIST)),
    ])
    client.authenticate('user@example.com', 'secret')
    assert waits == [10, 20]
    assert len(set(FakeSigner.last.payloads)) == 1
    assert [c['body']['attempt'] for c in client.sess.calls] == ['1'] * 3


def test_html_301_without_location_retries_only_original_endpoint():
    client = _client([FakeResponse(301, b'<html>Moved</html>', {'Content-Type': 'text/html'}),
                      FakeResponse(302, headers={'Location': POD_URL}),
                      FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret')
    assert [c['url'] for c in client.sess.calls] == [LEGACY_AUTH_URL, LEGACY_AUTH_URL, POD_URL]
    assert len(set(FakeSigner.last.payloads)) == 1


def test_html_301_without_location_remains_bounded():
    client = _client([FakeResponse(301, b'<html>Moved</html>') for _ in range(3)])
    with pytest.raises(StoreException, match='3 requests'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 3


def test_html_301_with_unsafe_location_fails_without_retry():
    client = _client([FakeResponse(301, b'<html>Moved</html>', {'Location': 'https://evil.example/'})])
    with pytest.raises(StoreException, match='endpoint'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1


@pytest.mark.parametrize('status', [403, 429, 503])
def test_populated_account_refusal_is_not_retried(status):
    failure = {'failureType': '1234', 'customerMessage': 'Incorrect password'}
    client = _client([FakeResponse(status, plistlib.dumps(failure))])
    with pytest.raises(StoreException, match='Incorrect password'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1


def test_retry_after_takes_precedence(monkeypatch):
    waits = []
    monkeypatch.setattr(store_mod.time, 'sleep', waits.append)
    client = _client([FakeResponse(429, headers={'Retry-After': '15'}),
                      FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret')
    assert waits == [15]


def test_retry_after_date_is_respected(monkeypatch):
    from email.utils import formatdate
    monkeypatch.setattr(store_mod.time, 'time', lambda: 1000)
    waits = []
    monkeypatch.setattr(store_mod.time, 'sleep', waits.append)
    client = _client([FakeResponse(429, headers={'Retry-After': formatdate(1025, usegmt=True)}),
                      FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret')
    assert waits == [25]


@pytest.mark.parametrize('value', ['31', '99999999999999999999999999999999999'])
def test_long_retry_after_stops_without_early_retry(value):
    client = _client([FakeResponse(429, headers={'Retry-After': value})])
    with pytest.raises(StoreException, match='longer wait'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1


@pytest.mark.parametrize('error', [requests.exceptions.Timeout, requests.exceptions.ConnectionError])
def test_transport_retry_is_bounded_and_sanitized(monkeypatch, error):
    calls = []
    def failed(*args, **kwargs):
        calls.append(args)
        raise error('private password signature')
    client = _client([])
    monkeypatch.setattr(client.sess, 'post', failed)
    with pytest.raises(StoreException, match='3 requests') as result:
        client.authenticate('user@example.com', 'secret')
    assert 'private' not in str(result.value)
    assert len(calls) == 3
    assert FakeSigner.last.closed


def test_certificate_error_is_not_retried_or_exposed(monkeypatch):
    calls = []
    def failed(*args, **kwargs):
        calls.append(args)
        raise requests.exceptions.SSLError('private request')
    client = _client([])
    monkeypatch.setattr(client.sess, 'post', failed)
    with pytest.raises(StoreException, match='TLS verification') as result:
        client.authenticate('user@example.com', 'secret')
    assert 'private' not in str(result.value)
    assert len(calls) == 1
    assert FakeSigner.last.closed


def test_relative_pod_redirect_is_validated():
    client = _client([FakeResponse(302, headers={'Location': '//p7-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?Pod=7'}),
                      FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'secret')
    assert client.sess.calls[1]['url'] == POD_URL.split('&PRH=7')[0]


@pytest.mark.parametrize('location', ['   ', '//evil.example/WebObjects/MZFinance.woa/wa/authenticate'])
def test_invalid_relative_redirect_never_receives_credentials(location):
    client = _client([FakeResponse(302, headers={'Location': location})])
    with pytest.raises(StoreException):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1


@pytest.mark.parametrize('flags,password', [
    (['--appstore_password', 'secret'], 'secret'),
    (['--appstore_password', 'secret', '--appstore_2FA', ''], 'secret'),
    (['--appstore_password', 'secret', '--appstore_2FA', '123 456'], 'secret123456'),
    (['--appstore_password2FA', 'secret123456'], 'secret123456'),
])
def test_cli_passes_password_to_real_download_boundary(monkeypatch, tmp_path, flags, password):
    from tests.conftest import run_main
    captured = []
    def download(self, directory, *args):
        captured.append(self.pass2FA)
        artifact = tmp_path / 'application.ipa'
        artifact.write_bytes(b'ipa download fixture')
        return str(artifact), 'md5'
    monkeypatch.setattr('mdast_cli.mdast_scan.AppStore.download_app', download)
    assert run_main(monkeypatch, ['--distribution_system', 'appstore', '--download_only',
                                 '--appstore_app_id', '1234', '--appstore_apple_id', 'user@example.com',
                                 '--download_path', str(tmp_path)] + flags) == 0
    assert captured == [password]


@pytest.mark.parametrize('status', [301, 302])
def test_redirect_without_location_is_rejected(status):
    client = _client([FakeResponse(status)])
    with pytest.raises(StoreException, match='no Location'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1


@pytest.mark.parametrize('url', [
    'https://evil.example/WebObjects/MZFinance.woa/wa/authenticate',
    'http://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate',
    'https://buy.itunes.apple.com.evil.example/WebObjects/MZFinance.woa/wa/authenticate',
    'https://user:pass@buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate',
    'https://buy.itunes.apple.com:8443/WebObjects/MZFinance.woa/wa/authenticate',
    'https://buy.itunes.apple.com/unexpected',
])
def test_redirect_does_not_forward_credentials_to_invalid_endpoint(url):
    client = _client([FakeResponse(302, headers={'Location': url})])
    with pytest.raises(StoreException, match='endpoint'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1
    assert FakeSigner.last.closed


def test_action_signature_covers_exact_request_bytes():
    client = _client([FakeResponse(200, plistlib.dumps(SUCCESS_PLIST))])
    client.authenticate('user@example.com', 'password123456')
    call = client.sess.calls[0]
    assert base64.b64decode(call['headers']['X-Apple-ActionSignature']) == b'signed:' + call['data']
    assert call['body']['password'] == 'password123456'
    assert call['verify'] is True
    assert call['allow_redirects'] is False


def test_current_response_shape_without_download_queue():
    data = dict(SUCCESS_PLIST, dsPersonId='4242')
    del data['download-queue-info']
    client = _client([FakeResponse(200, plistlib.dumps(data))])
    client.authenticate('user@example.com', 'secret')
    assert str(client.dsid) == '4242'


def test_redirect_loop_is_bounded():
    client = _client([FakeResponse(302, headers={'Location': POD_URL}) for _ in range(5)])
    with pytest.raises(StoreException, match='Too many'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 5


def test_two_factor_required_is_reported_without_retries():
    client = _client([FakeResponse(200, plistlib.dumps({'customerMessage': 'MZFinance.BadLogin.Configurator_message'}))])
    with pytest.raises(StoreException, match='BadLogin'):
        client.authenticate('user@example.com', 'secret')
    assert len(client.sess.calls) == 1
# --- purchase / download -----------------------------------------------------------
# buyProduct on MZBuy answers HTTP 200 with m-allowed=False for every app, so no license
# is ever created and the download that follows fails with failureType 9610. The license
# only gets created on the MZFinance path.

def _authed_client(responses):
    client = _client(responses)
    client.pod = "12"
    return client


def test_purchase_uses_mzfinance_path():
    client = _authed_client([FakeResponse(200, plistlib.dumps({"jingleDocType": "purchaseSuccess", "status": 0}))])

    assert client.purchase("310633997") is True
    assert client.sess.calls[0]["url"] == "https://p12-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/buyProduct"


def test_purchase_reports_already_owned():
    client = _authed_client([FakeResponse(200, plistlib.dumps({"failureType": "5002",
                                                               "customerMessage": "An unknown error has occurred"}))])

    assert client.purchase("310633997") is False


def test_purchase_rejection_is_not_reported_as_success():
    """HTTP 200 + m-allowed=False is a refusal; the old code logged it as a success."""
    refusal = {"failureType": "", "m-allowed": False, "cancel-purchase-batch": True,
               "customerMessage": "Unable to process your request."}
    client = _authed_client([FakeResponse(200, plistlib.dumps(refusal))])

    with pytest.raises(StoreException) as exc:
        client.purchase("310633997")

    assert "Unable to process your request." in str(exc.value)


def test_download_without_songlist_surfaces_failure_type():
    client = _authed_client([FakeResponse(200, plistlib.dumps({"failureType": "9610",
                                                               "customerMessage": "License not found."}))])

    with pytest.raises(StoreException) as exc:
        client.download("284882215")

    assert exc.value.err_type == "9610"
    assert "License not found." in str(exc.value)


def test_download_returns_song_list():
    payload = {"songList": [{"songId": 1, "URL": "https://example.invalid/app.ipa", "md5": "abc",
                             "metadata": {"bundleDisplayName": "App", "bundleShortVersionString": "1.0",
                                          "softwareVersionBundleId": "com.example.app"}}]}
    client = _authed_client([FakeResponse(200, plistlib.dumps(payload))])

    resp = client.download("389801252")

    assert len(resp.songList) == 1
    assert client.sess.calls[0]["url"].startswith(
        "https://p12-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct?guid=")


def test_5002_means_already_owned_on_purchase_but_a_random_failure_on_download():
    """Apple reuses failureType 5002 for two different things; the fix must not conflate them."""
    from mdast_cli.distribution_systems.appstore_client.store import (
        DOWNLOAD_RETRY_FAILURES, FAILURES_NEEDING_REAUTH, FAILURE_LICENSE_ALREADY_EXISTS)

    # Not a stale session: a fresh login does not clear it, so re-authenticating is wasted.
    assert FAILURE_LICENSE_ALREADY_EXISTS not in FAILURES_NEEDING_REAUTH
    assert FAILURE_LICENSE_ALREADY_EXISTS in DOWNLOAD_RETRY_FAILURES

    client = _authed_client([FakeResponse(200, plistlib.dumps({"failureType": "5002"}))])
    assert client.purchase("389801252") is False  # purchase: already owned, not an error


def test_download_info_retries_through_random_5002(monkeypatch):
    """Apple throws 5002 at random; repeating the same request clears it."""
    from mdast_cli.distribution_systems import appstore as appstore_mod

    monkeypatch.setattr(appstore_mod.time, "sleep", lambda *_: None)
    store = _authed_client([
        FakeResponse(200, plistlib.dumps({"failureType": "5002"})),
        FakeResponse(200, plistlib.dumps({"failureType": "5002"})),
        FakeResponse(200, plistlib.dumps({"songList": [{"songId": 1, "URL": "https://x.invalid",
                                                        "md5": "abc", "metadata": {}}]})),
    ])
    app = appstore_mod.AppStore.__new__(appstore_mod.AppStore)
    app.store = store

    resp = app._download_info_with_retries("389801252")

    assert len(resp.songList) == 1
    assert len(store.sess.calls) == 3  # two failures ridden out, no re-login


def test_download_info_buys_a_missing_license_then_retries(monkeypatch):
    from mdast_cli.distribution_systems import appstore as appstore_mod

    monkeypatch.setattr(appstore_mod.time, "sleep", lambda *_: None)
    store = _authed_client([
        FakeResponse(200, plistlib.dumps({"failureType": "9610", "customerMessage": "License not found."})),
        FakeResponse(200, plistlib.dumps({"jingleDocType": "purchaseSuccess", "status": 0})),
        FakeResponse(200, plistlib.dumps({"songList": [{"songId": 1, "URL": "https://x.invalid",
                                                        "md5": "abc", "metadata": {}}]})),
    ])
    app = appstore_mod.AppStore.__new__(appstore_mod.AppStore)
    app.store = store

    resp = app._download_info_with_retries("284882215")

    assert len(resp.songList) == 1
    assert "buyProduct" in store.sess.calls[1]["url"]


@pytest.mark.parametrize("raw,expected", [
    ("‎WhatsApp", "WhatsApp"),          # Apple ships a bidi mark in bundleDisplayName
    ("Instagram", "Instagram"),
    ("Foo/Bar", "FooBar"),                   # a separator would redirect the download path
    ("‎", "application"),               # nothing printable left
])
def test_sanitize_file_name(raw, expected):
    from mdast_cli.distribution_systems.appstore import sanitize_file_name
    assert sanitize_file_name(raw) == expected
