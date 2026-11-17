import logging

import pytest
import responses

from mdast_cli import ms_flow
from tests.conftest import REST_URL, run_main, scan_json
from tests.test_smoke_flows import ms_argv, register_ms_happy_path


@pytest.mark.parametrize('during_run', [False, True])
@pytest.mark.parametrize('manual', [False, True])
def test_cancelled_scan_finishes_without_timeout_or_reports(
        mocked_responses, monkeypatch, tmp_apk, apk_md5, no_sleep, ms_mode, caplog,
        during_run, manual):
    register_ms_happy_path(mocked_responses, apk_md5, with_testcase=not manual)
    mocked_responses.remove(responses.GET, f'{REST_URL}/scans/77/')
    if during_run:
        mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/', json=scan_json())
        if manual:
            mocked_responses.add(responses.POST, f'{REST_URL}/scans/77/stop/', json={})
    mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                         json=scan_json(stage='CANCELLED', status='COMPLETE'))
    monkeypatch.setattr(ms_flow, 'TRY', 3)
    with caplog.at_level(logging.INFO):
        result = run_main(monkeypatch, ms_argv(tmp_apk, with_testcase=not manual))
    reads = sum(c.request.url == f'{REST_URL}/scans/77/' and c.request.method == 'GET'
                for c in mocked_responses.calls)
    assert result == 5
    assert reads == (2 if during_run else 1)
    assert 'was cancelled' in caplog.text
    assert 'Scan did not start' not in caplog.text
    assert 'did not reach a terminal state' not in caplog.text
    assert not any('/report' in c.request.url for c in mocked_responses.calls)
    if not during_run:
        assert not any('/stop/' in c.request.url for c in mocked_responses.calls)


def test_cancelling_manual_scan_is_polled_without_stop(
        mocked_responses, monkeypatch, tmp_apk, apk_md5, no_sleep, ms_mode):
    register_ms_happy_path(mocked_responses, apk_md5, with_testcase=False)
    mocked_responses.remove(responses.GET, f'{REST_URL}/scans/77/')
    for status in ('PROCESSING', 'COMPLETE'):
        mocked_responses.add(responses.GET, f'{REST_URL}/scans/77/',
                             json=scan_json(stage='CANCELLED', status=status))
    assert not ms_flow.is_terminal({'stage': 'CANCELLED', 'status': 'PROCESSING'})
    assert run_main(monkeypatch, ms_argv(tmp_apk, with_testcase=False)) == 5
    assert not any('/stop/' in c.request.url for c in mocked_responses.calls)
