"""STG-5405: a lost start response must not create or start a second scan."""
from unittest import mock

import pytest
import requests

from mdast_cli import ms_flow
from mdast_cli.helpers.exit_codes import ExitCode

pytestmark = pytest.mark.unit


def response(code=200, payload=None):
    return mock.Mock(status_code=code, json=mock.Mock(return_value=payload))


def scan(stage='WORKING', status='WAITING', scan_id=77):
    return response(payload={'id': scan_id, 'stage': stage, 'status': status})


@pytest.mark.parametrize('result', [requests.ReadTimeout(), requests.ConnectionError(),
                                    response(409), response(502), response(503), response(504)])
def test_ambiguous_start_is_confirmed_without_another_post(result, no_sleep):
    client = mock.Mock()
    client.start_scan.side_effect = [result]
    client.get_scan_info.side_effect = [scan('CREATED', 'INITIAL'), scan('START', 'RENT_ENGINE')]
    ms_flow._start_scan(client, 77)
    client.start_scan.assert_called_once_with(77)
    client.create_auto_scan.assert_not_called()
    client.create_manual_scan.assert_not_called()
    assert client.get_scan_info.call_args_list == [mock.call(77), mock.call(77)]


def test_start_200_does_not_need_reconciliation():
    client = mock.Mock(start_scan=mock.Mock(return_value=response()))
    ms_flow._start_scan(client, 77)
    client.get_scan_info.assert_not_called()


@pytest.mark.parametrize('stage', ['START', 'WORKING', 'STOP', 'SUCCESS'])
def test_known_stages_confirm_start(stage):
    client = mock.Mock(start_scan=mock.Mock(side_effect=requests.ReadTimeout()),
                       get_scan_info=mock.Mock(return_value=scan(stage)))
    ms_flow._start_scan(client, 77)
    client.start_scan.assert_called_once_with(77)


@pytest.mark.parametrize('payload', [None, [], {}, {'id': 77},
                                    {'id': 77, 'stage': 'UNKNOWN', 'status': 'INITIAL'},
                                    {'id': 77, 'stage': 'START'},
                                    {'id': 77, 'stage': 'START', 'status': ''},
                                    {'id': 77, 'stage': 'WORKING', 'status': 'FAIL'},
                                    {'id': 78, 'stage': 'WORKING', 'status': 'WAITING'}])
def test_incomplete_or_unrelated_state_never_confirms_start(payload, caplog):
    client = mock.Mock(start_scan=mock.Mock(return_value=response(409)),
                       get_scan_info=mock.Mock(return_value=response(payload=payload)))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == ExitCode.NETWORK_ERROR
    assert 'Cannot confirm start of scan 77' in caplog.text
    client.start_scan.assert_called_once_with(77)


@pytest.mark.parametrize('stage', ['FAIL', 'CANCELLED'])
def test_failed_or_cancelled_scan_is_not_success(stage):
    client = mock.Mock(start_scan=mock.Mock(return_value=response(409)),
                       get_scan_info=mock.Mock(return_value=scan(stage)))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == ExitCode.SCAN_FAILED


@pytest.mark.parametrize('code', [401, 403])
@pytest.mark.parametrize('during_get', [True, False])
def test_auth_error_is_preserved(code, during_get):
    client = mock.Mock(start_scan=mock.Mock(return_value=response(409 if during_get else code)),
                       get_scan_info=mock.Mock(return_value=response(code)))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == ExitCode.AUTH_ERROR
    assert client.get_scan_info.call_count == int(during_get)


@pytest.mark.parametrize('conflict', [True, False])
def test_created_is_bounded_and_keeps_scan_id(conflict, no_sleep, caplog):
    client = mock.Mock(start_scan=mock.Mock(side_effect=[response(409) if conflict
                                                        else requests.ReadTimeout()]),
                       get_scan_info=mock.Mock(return_value=scan('CREATED', 'INITIAL')))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == (ExitCode.SCAN_FAILED if conflict else ExitCode.NETWORK_ERROR)
    assert client.get_scan_info.call_count == ms_flow.START_CONFIRM_ATTEMPTS
    client.start_scan.assert_called_once_with(77)
    assert 'Cannot confirm start of scan 77' in caplog.text


def test_transient_reads_share_single_retry_budget(no_sleep):
    client = mock.Mock(start_scan=mock.Mock(side_effect=requests.ReadTimeout()))
    client.get_scan_info.side_effect = [requests.ReadTimeout(), response(503), scan()]
    ms_flow._start_scan(client, 77)
    assert client.get_scan_info.call_count == 3
    client.start_scan.assert_called_once_with(77)


def test_read_network_errors_are_bounded(no_sleep, caplog):
    client = mock.Mock(start_scan=mock.Mock(side_effect=requests.ReadTimeout()),
                       get_scan_info=mock.Mock(side_effect=requests.ReadTimeout()))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == ExitCode.NETWORK_ERROR
    assert client.get_scan_info.call_count == ms_flow.START_CONFIRM_ATTEMPTS
    assert 'Cannot confirm start of scan 77' in caplog.text


def test_non_json_state_does_not_confirm_start(caplog):
    bad = response()
    bad.json.side_effect = ValueError('HTML gateway response')
    client = mock.Mock(start_scan=mock.Mock(side_effect=requests.ReadTimeout()),
                       get_scan_info=mock.Mock(return_value=bad))
    with pytest.raises(SystemExit) as exc:
        ms_flow._start_scan(client, 77)
    assert exc.value.code == ExitCode.NETWORK_ERROR
    assert 'Cannot confirm start of scan 77' in caplog.text
