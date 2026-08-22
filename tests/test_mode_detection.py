"""Unit tests for installation mode auto-detection and env override.

Auto-detection probes GET {base}/architectures/ and classifies by payload shape:
microservices = string type (ANDROID/IOS), monolith = int type code.
"""
import pytest
import requests
import responses

from mdast_cli_core.factory import (MODE_MICROSERVICES, MODE_MONOLITH, ModeDetectionError,
                                    resolve_installation_mode)
from tests.conftest import COMPANY_ID, REST_URL, TOKEN

pytestmark = pytest.mark.unit

ARCH_URL = f'{REST_URL}/architectures/'
MS_ARCH = [{'id': 1, 'type': 'ANDROID', 'os_version': '11', 'name': 'Android 11'}]
MS_ARCH_PAGE = {'items': MS_ARCH, 'total': 1, 'page': 1, 'size': 50, 'pages': 1}
MONO_ARCH = [{'id': 1, 'type': 1, 'name': 'Android 11'}]


def test_env_override_microservices(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'microservices')
    assert resolve_installation_mode(REST_URL, TOKEN, None) == MODE_MICROSERVICES


def test_env_override_monolith(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'monolith')
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MONOLITH


def test_env_invalid_value(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'quantum')
    with pytest.raises(ModeDetectionError):
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)


def test_autodetect_microservices_by_payload(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, json=MS_ARCH)  # Bearer probe
    assert resolve_installation_mode(REST_URL, TOKEN, None) == MODE_MICROSERVICES
    assert mocked_responses.calls[0].request.headers['Authorization'] == f'Bearer {TOKEN}'


def test_autodetect_microservices_by_paginated_payload(mocked_responses, monkeypatch):
    """STG-4892 wraps the Clark/Scanyon catalogue in a Page envelope."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, json=MS_ARCH_PAGE)
    assert resolve_installation_mode(REST_URL, TOKEN, None) == MODE_MICROSERVICES


def test_autodetect_monolith_by_payload(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    # Bearer probe -> monolith answers 401 (Token-only), then Token probe -> int type
    mocked_responses.add(responses.GET, ARCH_URL, status=401)
    mocked_responses.add(responses.GET, ARCH_URL, json=MONO_ARCH)
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MONOLITH
    assert mocked_responses.calls[1].request.headers['Authorization'] == f'Token {TOKEN}'


def test_monolith_200_on_bearer_not_misclassified(mocked_responses, monkeypatch):
    """A monolith (int-type payload) answering 200 to the Bearer probe must NOT be
    read as microservices - classification is by payload shape, not status."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, json=MONO_ARCH)   # Bearer -> monolith shape
    mocked_responses.add(responses.GET, ARCH_URL, json=MONO_ARCH)   # Token  -> monolith shape
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MONOLITH


def test_ambiguous_200_payload_raises(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, json={'unexpected': 'shape'})
    mocked_responses.add(responses.GET, ARCH_URL, json={'unexpected': 'shape'})
    with pytest.raises(ModeDetectionError):
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)


def test_autodetect_failure_reports_auth_error(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, status=401)
    mocked_responses.add(responses.GET, ARCH_URL, status=401)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert excinfo.value.auth_error is True


def test_autodetect_failure_network(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, status=404)
    mocked_responses.add(responses.GET, ARCH_URL, status=500)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert excinfo.value.auth_error is False


# --- TLS-inspecting proxy: detection must not block a flow that does not verify ---

def test_tls_failure_falls_back_to_unverified_probe(mocked_responses, monkeypatch):
    """A TLS-inspecting proxy must not block a monolith run.

    The monolith flow itself sends every request with verify=False, so failing the
    detection probe on certificate verification blocks a door with no wall behind it.
    """
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    # Verified probes (Bearer, then Token) both fail the handshake...
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError(
        'certificate verify failed: self-signed certificate in certificate chain'))
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError(
        'certificate verify failed: self-signed certificate in certificate chain'))
    # ...the unverified retry succeeds and classifies the stand.
    mocked_responses.add(responses.GET, ARCH_URL, status=401)
    mocked_responses.add(responses.GET, ARCH_URL, json=MONO_ARCH)
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MONOLITH
    assert mocked_responses.calls[-1].request.req_kwargs['verify'] is False


def test_tls_fallback_does_not_silently_accept_microservices(mocked_responses, monkeypatch):
    """Microservices verify certificates for real traffic, so resolving the mode over
    an unverified channel would only defer the failure - demand an explicit decision."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError('boom'))
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError('boom'))
    mocked_responses.add(responses.GET, ARCH_URL, json=MS_ARCH)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert 'REQUESTS_CA_BUNDLE' in str(excinfo.value)


def test_no_tls_fallback_when_verification_already_disabled(mocked_responses, monkeypatch):
    """With verify=False there is nothing to fall back from - do not probe twice."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError('boom'))
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.SSLError('boom'))
    with pytest.raises(ModeDetectionError):
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID, verify=False)
    assert len(mocked_responses.calls) == 2


# --- diagnosis: name the real cause instead of blaming --url/--token ---

def test_proxy_error_points_at_proxy_env_vars(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.ProxyError(
        'Unable to connect to proxy'))
    mocked_responses.add(responses.GET, ARCH_URL, body=requests.exceptions.ProxyError(
        'Unable to connect to proxy'))
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    message = str(excinfo.value)
    assert 'HTTPS_PROXY' in message
    assert '--token' not in message


def test_auth_failure_quotes_server_explanation(mocked_responses, monkeypatch):
    """The server says 'Token has expired' - that must reach the operator."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    body = {'message': 'Token has expired', 'detail': [{'code': 900}]}
    mocked_responses.add(responses.GET, ARCH_URL, json=body, status=401)
    mocked_responses.add(responses.GET, ARCH_URL, json=body, status=401)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert 'Token has expired' in str(excinfo.value)
    assert excinfo.value.auth_error is True


def test_quoted_body_never_leaks_the_token(mocked_responses, monkeypatch):
    """A server that echoes the credential back must not turn diagnostics into a leak."""
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    body = {'message': f'Invalid token: {TOKEN}'}
    mocked_responses.add(responses.GET, ARCH_URL, json=body, status=401)
    mocked_responses.add(responses.GET, ARCH_URL, json=body, status=401)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert TOKEN not in str(excinfo.value)
    assert '***' in str(excinfo.value)
