"""Unit tests for installation mode auto-detection and env override."""
import pytest
import responses

from mdast_cli_core.factory import (MODE_MICROSERVICES, MODE_MONOLITH, ModeDetectionError,
                                    resolve_installation_mode)
from tests.conftest import COMPANY_ID, REST_URL, TOKEN

pytestmark = pytest.mark.unit


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


def test_autodetect_microservices(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', json=[])
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MICROSERVICES
    probe = mocked_responses.calls[0].request
    assert probe.headers['Authorization'] == f'Bearer {TOKEN}'


def test_autodetect_monolith_fallback(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', status=404)
    mocked_responses.add(responses.GET, f'{REST_URL}/organizations/{COMPANY_ID}/engines/',
                         json=[])
    assert resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID) == MODE_MONOLITH
    monolith_probe = mocked_responses.calls[1].request
    assert monolith_probe.headers['Authorization'] == f'Token {TOKEN}'


def test_autodetect_failure_reports_auth_error(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', status=401)
    mocked_responses.add(responses.GET, f'{REST_URL}/organizations/{COMPANY_ID}/engines/',
                         status=401)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert excinfo.value.auth_error is True


def test_autodetect_failure_network(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    mocked_responses.add(responses.GET, f'{REST_URL}/engines/', status=404)
    mocked_responses.add(responses.GET, f'{REST_URL}/organizations/{COMPANY_ID}/engines/',
                         status=500)
    with pytest.raises(ModeDetectionError) as excinfo:
        resolve_installation_mode(REST_URL, TOKEN, COMPANY_ID)
    assert excinfo.value.auth_error is False
