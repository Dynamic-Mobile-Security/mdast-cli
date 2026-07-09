"""Unit tests for installation mode auto-detection and env override.

Auto-detection probes GET {base}/architectures/ and classifies by payload shape:
microservices = string type (ANDROID/IOS), monolith = int type code.
"""
import pytest
import responses

from mdast_cli_core.factory import (MODE_MICROSERVICES, MODE_MONOLITH, ModeDetectionError,
                                    resolve_installation_mode)
from tests.conftest import COMPANY_ID, REST_URL, TOKEN

pytestmark = pytest.mark.unit

ARCH_URL = f'{REST_URL}/architectures/'
MS_ARCH = [{'id': 1, 'type': 'ANDROID', 'os_version': '11', 'name': 'Android 11'}]
MONO_ARCH = [{'id': 1, 'type': 1, 'name': 'Android 11'}]


def test_env_override_microservices(monkeypatch):
    monkeypatch.setenv('MDAST_CLI_MODE', 'microservices')
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MICROSERVICES


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
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MICROSERVICES
    assert mocked_responses.calls[0].request.headers['Authorization'] == f'Bearer {TOKEN}'


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
