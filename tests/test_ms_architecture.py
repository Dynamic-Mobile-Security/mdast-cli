"""Unit tests for microservices OS-version selection (STG-4588)."""

import pytest

from mdast_cli.helpers.const import OS_ANDROID, OS_IOS
from mdast_cli.ms_flow import resolve_ms_os_version

pytestmark = pytest.mark.unit


def test_prefers_default_architecture_name():
    architectures = [
        {'type': 'ANDROID', 'os_version': '14', 'name': 'Android 14'},
        {'type': 'ANDROID', 'os_version': '11', 'name': 'Android 11'},
    ]

    assert resolve_ms_os_version(architectures, OS_ANDROID) == '11'


def test_falls_back_to_first_platform_version():
    architectures = [
        {'type': 'ANDROID', 'os_version': '14', 'name': 'Android 14'},
        {'type': 'IOS', 'os_version': '16', 'name': 'iOS 16'},
    ]

    assert resolve_ms_os_version(architectures, OS_IOS) == '16'


@pytest.mark.parametrize('architectures', [None, {}, [], [{'type': 'ANDROID', 'os_version': ''}]])
def test_missing_platform_version_returns_none(architectures):
    assert resolve_ms_os_version(architectures, OS_ANDROID) is None
