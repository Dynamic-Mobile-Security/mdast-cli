"""Security-focused tests: secrets handling, server-controlled inputs, TLS."""
import logging
import os
from unittest import mock

import pytest
import responses

from mdast_cli_core import factory
from mdast_cli_core.microservices import mDastMicroservices
from tests.conftest import BASE_URL, REST_URL, TOKEN, application_json, run_main, scan_json
from tests.test_smoke_flows import ms_argv, register_ms_happy_path

pytestmark = pytest.mark.security


def test_token_never_appears_in_logs(mocked_responses, monkeypatch, tmp_path, tmp_apk,
                                     apk_md5, no_sleep, ms_mode, caplog, capsys):
    """The org token is a credential: it must not leak to logs, stdout or stderr."""
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5)
    with caplog.at_level(logging.DEBUG):
        exit_code = run_main(monkeypatch, ms_argv(tmp_apk) + ['--verbose'])
    assert exit_code == 0
    for record in caplog.records:
        assert TOKEN not in record.getMessage()
    captured = capsys.readouterr()
    assert TOKEN not in captured.out
    assert TOKEN not in captured.err


def test_token_never_in_urls(mocked_responses, monkeypatch, tmp_path, tmp_apk, apk_md5,
                             no_sleep, ms_mode):
    """The token travels only in the Authorization header, never in a URL/query."""
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5)
    run_main(monkeypatch, ms_argv(tmp_apk))
    for call in mocked_responses.calls:
        assert TOKEN not in call.request.url
        assert call.request.headers['Authorization'] == f'Bearer {TOKEN}'


def test_content_disposition_cannot_control_local_path(mocked_responses, monkeypatch,
                                                       tmp_path, tmp_apk, apk_md5,
                                                       no_sleep, ms_mode):
    """A hostile/compromised server must not choose where the CLI writes files.

    Report file names come from CLI arguments only; Content-Disposition
    (path traversal attempt here) is ignored.
    """
    monkeypatch.chdir(tmp_path)
    register_ms_happy_path(mocked_responses, apk_md5)
    mocked_responses.replace(
        responses.GET, f'{REST_URL}/scans/77/report', body=b'%PDF-1.4 fake',
        headers={'Content-Disposition': 'attachment; filename="../../../../tmp/evil.pdf"'})
    exit_code = run_main(monkeypatch, ms_argv(tmp_apk))
    assert exit_code == 0
    written = sorted(p.name for p in tmp_path.iterdir())
    assert 'scan_report_pdf.pdf' in written
    assert not any('evil' in name for name in written)
    assert not os.path.exists('/tmp/evil.pdf')


def test_x_file_size_matches_actual_content(mocked_responses, tmp_apk):
    """Anti request smuggling consistency: X-File-Size equals the real binary size."""
    mocked_responses.add(responses.POST, f'{REST_URL}/applications/upload_info/',
                         json={'id': 1}, status=201)
    client = mDastMicroservices(REST_URL, TOKEN)
    client.upload_application(tmp_apk)
    request = mocked_responses.calls[-1].request
    declared = int(request.headers['X-File-Size'])
    assert declared == os.path.getsize(tmp_apk)
    assert declared <= int(request.headers['Content-Length'])


def test_tls_verify_enabled_by_default():
    """F4: secure by default - client verifies TLS unless explicitly told not to."""
    client = mDastMicroservices(REST_URL, TOKEN)
    with mock.patch('mdast_cli_core.microservices.requests.get') as mocked_get:
        client.get_architectures()
    assert mocked_get.call_args.kwargs['verify'] is True


def test_tls_verify_can_be_disabled_via_client_flag():
    client = mDastMicroservices(REST_URL, TOKEN, verify=False)
    with mock.patch('mdast_cli_core.microservices.requests.get') as mocked_get:
        client.get_architectures()
    assert mocked_get.call_args.kwargs['verify'] is False


@pytest.mark.parametrize('raw,expected', [
    # secure by default: unset/empty -> True; only explicit off-values disable
    (None, True), ('1', True), ('true', True), ('YES', True), ('on', True), ('', True),
    ('0', False), ('false', False), ('no', False), ('off', False),
])
def test_tls_verify_env_parsing(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv(factory.TLS_VERIFY_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(factory.TLS_VERIFY_ENV_VAR, raw)
    assert factory.tls_verify_enabled() is expected


def test_precheck_payload_with_control_characters_is_safe():
    """Warning payload is server-controlled: rendering must be json-escaped, one line."""
    from mdast_cli.ms_flow import render_precheck_warning
    line = render_precheck_warning({
        'type': 'empty_profile',
        'payload': {'note': 'line1\nline2\x1b[31mred'},
    })
    assert '\n' not in line
    assert '\x1b' not in line


def test_mode_probe_does_not_leak_token_on_error(mocked_responses, monkeypatch):
    monkeypatch.delenv('MDAST_CLI_MODE', raising=False)
    # The factory probes GET /architectures/ (Bearer, then Token) - both 401 here.
    # One registration serves both probes (responses reuses it for repeat calls).
    mocked_responses.add(responses.GET, f'{REST_URL}/architectures/', status=401)
    with pytest.raises(factory.ModeDetectionError) as excinfo:
        factory.resolve_installation_mode(REST_URL, TOKEN, '1')
    # An auth failure must be classified as such, and the token must never appear
    # in the surfaced error (it is logged/raised near the Authorization header).
    assert excinfo.value.auth_error is True
    assert TOKEN not in str(excinfo.value)
