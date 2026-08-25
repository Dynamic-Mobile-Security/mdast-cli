"""Regression tests for the App Store authentication flow.

Apple broke the native auth endpoint in July 2026: it answers 204/403/404/503 with an
empty, non-plist body. The working flow (mirrored from majd/ipatool#514) is:

    native /auth/v1/native/fast/  -> 204/403/404/503
    legacy MZFinance authenticate -> 302 Location: https://pN-buy.itunes.apple.com/...
    repost the SAME plist body (attempt still 1) to the pod URL -> 200 + plist
"""
import plistlib

import pytest

from mdast_cli.distribution_systems.appstore_client import store as store_mod
from mdast_cli.distribution_systems.appstore_client.store import (
    LEGACY_AUTH_URL,
    StoreClient,
    StoreException,
    _normalize_auth_endpoint,
)

POD_URL = "https://p7-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?Pod=7&PRH=7"

SUCCESS_PLIST = {
    "m-allowed": True,
    "passwordToken": "token-123",
    "download-queue-info": {"dsid": 4242},
    "accountInfo": {"address": {"firstName": "Test", "lastName": "User"}},
}


class FakeResponse:
    def __init__(self, status_code, content=b"", headers=None, url=""):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self.url = url
        self.text = content.decode("utf-8", "replace")


class FakeSession:
    """Records POSTs and replays a scripted list of responses."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.headers = {}
        self.calls = []

    def post(self, url, headers=None, data=None, **kwargs):
        self.calls.append({"url": url, "body": plistlib.loads(data)})
        return self._responses.pop(0)


def _client(responses):
    client = StoreClient(FakeSession(responses), guid="12367150C7F5")
    return client


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(store_mod.time, "sleep", lambda *_: None)


@pytest.fixture
def _bag_returns_legacy(monkeypatch):
    monkeypatch.setattr(StoreClient, "get_bag", lambda self: LEGACY_AUTH_URL)


@pytest.mark.parametrize(
    "endpoint,expected",
    [
        ("https://auth.itunes.apple.com/auth/v1/native/fast", "https://auth.itunes.apple.com/auth/v1/native/fast/"),
        ("https://auth.itunes.apple.com/auth/v1/native/fast/", "https://auth.itunes.apple.com/auth/v1/native/fast/"),
        (LEGACY_AUTH_URL, LEGACY_AUTH_URL),
        (None, None),
    ],
)
def test_normalize_auth_endpoint(endpoint, expected):
    assert _normalize_auth_endpoint(endpoint) == expected


def test_pod_redirect_reposts_body_with_attempt_one(_bag_returns_legacy):
    """Apple rejects the pod repost if `attempt` is bumped, so it must stay 1."""
    client = _client([
        FakeResponse(302, headers={"Location": POD_URL}),
        FakeResponse(200, plistlib.dumps(SUCCESS_PLIST), headers={"pod": "7"}, url=POD_URL),
    ])

    resp = client.authenticate("user@example.com", "secret123456")

    assert resp.passwordToken == "token-123"
    assert client.account_name == "Test User"
    assert client.pod == "7"
    urls = [c["url"] for c in client.sess.calls]
    assert urls == [LEGACY_AUTH_URL, POD_URL]
    assert [c["body"]["attempt"] for c in client.sess.calls] == ["1", "1"]
    assert client.sess.calls[0]["body"] == client.sess.calls[1]["body"]


@pytest.mark.parametrize("status", [204, 403, 404, 503])
def test_falls_back_to_next_endpoint_on_empty_body(monkeypatch, status):
    """A non-plist body on the bag endpoint must not abort the login."""
    monkeypatch.setattr(StoreClient, "get_bag", lambda self: "https://auth.itunes.apple.com/auth/v1/native/fast/")
    client = _client([
        FakeResponse(status, b""),
        FakeResponse(302, headers={"Location": POD_URL}),
        FakeResponse(200, plistlib.dumps(SUCCESS_PLIST), url=POD_URL),
    ])

    client.authenticate("user@example.com", "secret123456")

    urls = [c["url"] for c in client.sess.calls]
    assert urls == ["https://auth.itunes.apple.com/auth/v1/native/fast/", LEGACY_AUTH_URL, POD_URL]
    assert client.pod == "7"  # derived from the pod URL when the header is absent


def test_invalid_credentials_are_reported_not_retried_forever(_bag_returns_legacy):
    failure = {"m-allowed": False, "customerMessage": "Your Apple ID or password was incorrect.",
               "failureType": "1234"}
    client = _client([FakeResponse(200, plistlib.dumps(failure))])

    with pytest.raises(StoreException) as exc:
        client.authenticate("user@example.com", "wrong")

    assert "incorrect" in str(exc.value)
    assert len(client.sess.calls) == 1


def test_first_attempt_invalid_credentials_is_retried_once(_bag_returns_legacy):
    """Apple spuriously fails attempt 1 with -5000; attempt 2 clears it."""
    failure = {"m-allowed": False, "customerMessage": "retry", "failureType": "-5000"}
    client = _client([
        FakeResponse(200, plistlib.dumps(failure)),
        FakeResponse(200, plistlib.dumps(SUCCESS_PLIST)),
    ])

    client.authenticate("user@example.com", "secret123456")

    assert [c["body"]["attempt"] for c in client.sess.calls] == ["1", "2"]


def test_all_endpoints_blocked_raises_actionable_error(_bag_returns_legacy):
    client = _client([FakeResponse(403, b"") for _ in range(2 * store_mod.AUTH_MAX_ROUNDS)])

    with pytest.raises(StoreException) as exc:
        client.authenticate("user@example.com", "secret123456")

    assert "Apple-side/network block" in str(exc.value)


@pytest.mark.parametrize("status", [301, 302])
def test_redirect_without_location_is_retried(_bag_returns_legacy, status):
    """Apple's edge emits bare 30x responses with no Location; that must not abort login."""
    client = _client([
        FakeResponse(status, b""),                       # bag/legacy endpoint, broken redirect
        FakeResponse(status, b""),                       # native endpoint, same
        FakeResponse(302, headers={"Location": POD_URL}),  # next round: real redirect
        FakeResponse(200, plistlib.dumps(SUCCESS_PLIST), url=POD_URL),
    ])

    client.authenticate("user@example.com", "secret123456")

    assert [c["url"] for c in client.sess.calls][-1] == POD_URL
