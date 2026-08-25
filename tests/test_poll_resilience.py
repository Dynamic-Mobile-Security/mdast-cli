"""Poll resilience: transient downstream 5xx during scan polling must be retried,
not fatal (a long CI poll should survive flaky blips while the scan keeps running)."""
from unittest import mock

import pytest
import requests
import responses

from mdast_cli.helpers.exit_codes import ExitCode
from mdast_cli import ms_flow
from mdast_cli_core.microservices import mDastMicroservices
from tests.conftest import REST_URL, TOKEN

pytestmark = pytest.mark.unit

SCAN_URL = f'{REST_URL}/scans/55/'


@pytest.fixture
def client():
    return mDastMicroservices(REST_URL, TOKEN)


def test_transient_502_then_success(client, mocked_responses, no_sleep):
    mocked_responses.add(responses.GET, SCAN_URL, status=502,
                         json={'error_code': 'downstream_unavailable', 'message': 'x'})
    mocked_responses.add(responses.GET, SCAN_URL, status=503, json={'error_code': 'busy'})
    mocked_responses.add(responses.GET, SCAN_URL,
                         json={'id': 55, 'stage': 'WORKING', 'status': 'PROCESSING'})
    scan = ms_flow._get_scan(client, 55)
    assert scan['stage'] == 'WORKING'


def test_persistent_502_exits_network_error(client, mocked_responses, no_sleep):
    for _ in range(ms_flow.POLL_TRANSIENT_RETRIES + 1):
        mocked_responses.add(responses.GET, SCAN_URL, status=502,
                             json={'error_code': 'downstream_unavailable', 'message': 'x'})
    with pytest.raises(SystemExit) as excinfo:
        ms_flow._get_scan(client, 55)
    assert excinfo.value.code == ExitCode.NETWORK_ERROR


def test_404_is_not_retried(client, mocked_responses, no_sleep):
    mocked_responses.add(responses.GET, SCAN_URL, status=404, json={'error_code': 'not_found'})
    with pytest.raises(SystemExit):
        ms_flow._get_scan(client, 55)
    # only one call - 404 is terminal, not retried
    assert len([c for c in mocked_responses.calls if c.request.url == SCAN_URL]) == 1


def test_network_exception_retried_then_success(client, no_sleep):
    resp_ok = mock.Mock(status_code=200)
    resp_ok.json.return_value = {'id': 55, 'stage': 'SUCCESS', 'status': 'COMPLETE'}
    seq = [requests.ConnectionError('boom'), resp_ok]
    with mock.patch.object(client, 'get_scan_info', side_effect=seq):
        scan = ms_flow._get_scan(client, 55)
    assert scan['status'] == 'COMPLETE'


# --- report download resilience (soft-fail contract, STG-4478) ---

REPORT_URL = f'{REST_URL}/scans/55/report'


def test_report_transient_502_then_success(client, mocked_responses, no_sleep):
    """A transient 502 on the report service is retried, then the PDF is returned."""
    mocked_responses.add(responses.GET, REPORT_URL, status=502, json={'error_code': 'busy'})
    mocked_responses.add(responses.GET, REPORT_URL, body=b'%PDF-1.4 x',
                         content_type='application/pdf')
    resp = ms_flow._download_report(client.download_report, 55, 'PDF report')
    assert resp is not None
    assert resp.content == b'%PDF-1.4 x'


def test_report_persistent_failure_soft_fails_to_none(client, mocked_responses, no_sleep):
    """A report that never renders returns None (soft-fail) - it must NOT raise:
    the scan already succeeded, so a report-service outage cannot turn it red."""
    for _ in range(ms_flow.POLL_TRANSIENT_RETRIES + 1):
        mocked_responses.add(responses.GET, REPORT_URL, status=502, json={'error_code': 'busy'})
    resp = ms_flow._download_report(client.download_report, 55, 'PDF report')
    assert resp is None


def test_report_network_exception_then_success(client, no_sleep):
    """A raw connection drop on report fetch is retried, not fatal."""
    resp_ok = mock.Mock(status_code=200, content=b'%PDF-1.4 x')
    seq = [requests.ConnectionError('boom'), resp_ok]
    fetch = mock.Mock(side_effect=seq)
    resp = ms_flow._download_report(fetch, 55, 'PDF report')
    assert resp is resp_ok


def test_report_202_then_202_then_success(client, mocked_responses, monkeypatch):
    """Async report preparation is polled until the final 200 response."""
    sleeps = []
    monkeypatch.setattr(ms_flow.time, 'sleep', sleeps.append)
    mocked_responses.add(responses.GET, REPORT_URL, status=202,
                         headers={'Retry-After': '30'})
    mocked_responses.add(responses.GET, REPORT_URL, status=202)
    mocked_responses.add(responses.GET, REPORT_URL, body=b'%PDF-1.4 x',
                         content_type='application/pdf')

    resp = ms_flow._download_report(client.download_report, 55, 'PDF report',
                                    report_timeout=120)

    assert resp is not None
    assert resp.content == b'%PDF-1.4 x'
    assert sleeps == [30, ms_flow.SLEEP_TIMEOUT]


def test_report_202_does_not_consume_transient_retry_budget(client, mocked_responses,
                                                            no_sleep, monkeypatch):
    """HTTP 202 is a normal pending state, not one of transient retry attempts."""
    monkeypatch.setattr(ms_flow, 'POLL_TRANSIENT_RETRIES', 2)
    for _ in range(5):
        mocked_responses.add(responses.GET, REPORT_URL, status=202)
    mocked_responses.add(responses.GET, REPORT_URL, body=b'%PDF-1.4 x',
                         content_type='application/pdf')

    resp = ms_flow._download_report(client.download_report, 55, 'PDF report',
                                    report_timeout=120)

    assert resp is not None
    assert len([c for c in mocked_responses.calls if c.request.url.startswith(REPORT_URL)]) == 6


def test_report_invalid_retry_after_uses_default_sleep(client, mocked_responses, monkeypatch):
    """Retry-After is deliberately supported only as integer seconds."""
    sleeps = []
    monkeypatch.setattr(ms_flow.time, 'sleep', sleeps.append)
    mocked_responses.add(responses.GET, REPORT_URL, status=202,
                         headers={'Retry-After': 'later'})
    mocked_responses.add(responses.GET, REPORT_URL, body=b'%PDF-1.4 x',
                         content_type='application/pdf')

    resp = ms_flow._download_report(client.download_report, 55, 'PDF report',
                                    report_timeout=120)

    assert resp is not None
    assert sleeps == [ms_flow.SLEEP_TIMEOUT]


def test_report_202_timeout_soft_fails_to_none(monkeypatch):
    """A report that stays pending past the report timeout remains a soft-fail."""
    resp_pending = mock.Mock(status_code=202, headers={})
    fetch = mock.Mock(return_value=resp_pending)
    monotonic_values = iter([0, 2])
    monkeypatch.setattr(ms_flow.time, 'monotonic', lambda: next(monotonic_values))

    resp = ms_flow._download_report(fetch, 55, 'PDF report', report_timeout=1)

    assert resp is None
    assert fetch.call_count == 1


def test_report_202_then_transient_then_success(client, mocked_responses, no_sleep):
    """Transient failures during async report waiting use their own retry budget."""
    mocked_responses.add(responses.GET, REPORT_URL, status=202)
    mocked_responses.add(responses.GET, REPORT_URL, status=502, json={'error_code': 'busy'})
    mocked_responses.add(responses.GET, REPORT_URL, status=202)
    mocked_responses.add(responses.GET, REPORT_URL, body=b'%PDF-1.4 x',
                         content_type='application/pdf')

    resp = ms_flow._download_report(client.download_report, 55, 'PDF report',
                                    report_timeout=120)

    assert resp is not None
    assert resp.content == b'%PDF-1.4 x'
