"""Unit/contract tests for the pre-check gate (DEC-671-05) and warning rendering."""
import pytest
import responses

from mdast_cli.helpers.exit_codes import ExitCode
from mdast_cli.ms_flow import render_precheck_warning, run_precheck_gate
from mdast_cli_core.microservices import mDastMicroservices
from tests.conftest import REST_URL, TOKEN

pytestmark = [pytest.mark.unit, pytest.mark.contract]

PRECHECK_URL = f'{REST_URL}/scans/start/precheck/'


@pytest.fixture
def client():
    return mDastMicroservices(REST_URL, TOKEN)


def test_empty_warnings_pass(client, mocked_responses):
    mocked_responses.add(responses.POST, PRECHECK_URL, json={'warnings': []})
    run_precheck_gate(client, 'a' * 32, profile_id=1, testcase_id=None, scan_type='MANUAL')


def test_warnings_block_with_exit_code_8(client, mocked_responses, capsys):
    mocked_responses.add(responses.POST, PRECHECK_URL, json={'warnings': [
        {'type': 'empty_profile', 'payload': {}},
        {'type': 'architecture_unsupported',
         'payload': {'platform': 'Android', 'os_version': '99'}},
    ]})
    with pytest.raises(SystemExit) as excinfo:
        run_precheck_gate(client, 'a' * 32, profile_id=1, testcase_id=None, scan_type='MANUAL')
    assert excinfo.value.code == ExitCode.PRECHECK_BLOCKED == 8
    stderr = capsys.readouterr().err
    assert '[empty_profile]' in stderr
    assert '[architecture_unsupported]' in stderr
    assert '"os_version": "99"' in stderr


def test_precheck_unavailable_blocks(client, mocked_responses):
    """precheck_unavailable is a blocking warning too (STG-4475)."""
    mocked_responses.add(responses.POST, PRECHECK_URL, json={'warnings': [
        {'type': 'precheck_unavailable',
         'payload': {'unavailable_dependencies': ['application_lookup']}},
    ]})
    with pytest.raises(SystemExit) as excinfo:
        run_precheck_gate(client, 'a' * 32, profile_id=1, testcase_id=None, scan_type='MANUAL')
    assert excinfo.value.code == ExitCode.PRECHECK_BLOCKED


def test_precheck_transport_error_blocks(client, mocked_responses):
    mocked_responses.add(responses.POST, PRECHECK_URL, status=502,
                         json={'error_code': 'downstream_unavailable', 'message': 'Scanyon down'})
    with pytest.raises(SystemExit) as excinfo:
        run_precheck_gate(client, 'a' * 32, profile_id=1, testcase_id=None, scan_type='MANUAL')
    assert excinfo.value.code == ExitCode.PRECHECK_BLOCKED


def test_profile_not_found_fails(client, mocked_responses):
    mocked_responses.add(responses.POST, PRECHECK_URL, status=404,
                         json={'error_code': 'not_found', 'message': 'profile not found'})
    with pytest.raises(SystemExit) as excinfo:
        run_precheck_gate(client, 'a' * 32, profile_id=42, testcase_id=None, scan_type='MANUAL')
    assert excinfo.value.code == ExitCode.SCAN_FAILED


def test_missing_profile_id_skips_on_422(client, mocked_responses, caplog):
    """Interim behavior until scanyon makes profile_id optional: 422 + no profile -> skip."""
    mocked_responses.add(responses.POST, PRECHECK_URL, status=422,
                         json={'error_code': 'validation_error', 'message': 'profile_id required'})
    run_precheck_gate(client, 'a' * 32, profile_id=None, testcase_id=None, scan_type='MANUAL')
    assert any('pre-check skipped' in record.message.lower() for record in caplog.records)


def test_unknown_warning_type_rendered_generically():
    """Contract extension is backward-compatible: unknown types must not crash (DEC-666-04)."""
    line = render_precheck_warning({'type': 'brand_new_rule', 'payload': {'x': 1}})
    assert '[brand_new_rule]' in line
    assert '"x": 1' in line


def test_warning_without_payload_rendered():
    line = render_precheck_warning({'type': 'empty_profile'})
    assert '[empty_profile]' in line


def test_malformed_warning_rendered():
    line = render_precheck_warning({})
    assert '[unknown]' in line
