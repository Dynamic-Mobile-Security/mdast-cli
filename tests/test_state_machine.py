"""Unit tests for the scanyon-native (stage, status) state machine helpers."""
import pytest

from mdast_cli.helpers.const import TERMINAL_SCAN_PAIRS
from mdast_cli.ms_flow import is_success, is_terminal, resolve_platform, scan_pair

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('stage,status', sorted(TERMINAL_SCAN_PAIRS))
def test_terminal_pairs(stage, status):
    assert is_terminal({'stage': stage, 'status': status})


@pytest.mark.parametrize('stage,status', [
    ('CREATED', 'INITIAL'),
    ('START', 'PROCESSING'),
    ('WORKING', 'PROCESSING'),
    ('WORKING', 'WAITING'),
    ('STOP', 'INITIAL'),
    ('STOP', 'PROCESSING'),
    # STOP is transitional even with COMPLETE status: the FSM proceeds to SUCCESS
    ('STOP', 'COMPLETE'),
    ('SUCCESS', 'PROCESSING'),
    ('FAIL', 'PROCESSING'),
])
def test_non_terminal_pairs(stage, status):
    assert not is_terminal({'stage': stage, 'status': status})


def test_success_complete():
    assert is_success({'stage': 'SUCCESS', 'status': 'COMPLETE'})


def test_success_partial_complete():
    assert is_success({'stage': 'SUCCESS', 'status': 'PARTIAL_COMPLETE'})


def test_fail_is_not_success():
    assert not is_success({'stage': 'FAIL', 'status': 'FAIL'})


def test_scan_pair_missing_fields():
    assert scan_pair({}) == (None, None)
    assert not is_terminal({})


@pytest.mark.parametrize('file_name,expected', [
    ('app.apk', 'ANDROID'),
    ('app.aab', 'ANDROID'),
    ('app.apks', 'ANDROID'),
    ('app.zip', 'ANDROID'),
    ('app.ipa', 'IOS'),
    ('app.exe', None),
])
def test_resolve_platform(file_name, expected):
    assert resolve_platform(f'/tmp/{file_name}') == expected
