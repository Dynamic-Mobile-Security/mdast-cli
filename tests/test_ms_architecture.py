"""Unit tests for microservices OS-version selection (STG-4588)."""

from itertools import permutations

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


def test_selects_version_from_paginated_scanyon_catalogue():
    architectures = {
        'items': [
            {'type': 'ANDROID', 'os_version': '14', 'name': 'Android 14'},
            {'type': 'ANDROID', 'os_version': '11', 'name': 'Android 11'},
        ],
        'total': 2,
        'page': 1,
        'size': 50,
        'pages': 1,
    }

    assert resolve_ms_os_version(architectures, OS_ANDROID) == '11'


@pytest.mark.parametrize('architectures', [None, {}, [], [{'type': 'ANDROID', 'os_version': ''}]])
def test_missing_platform_version_returns_none(architectures):
    assert resolve_ms_os_version(architectures, OS_ANDROID) is None


@pytest.mark.parametrize('versions,expected', [
    *[(versions, '16') for versions in permutations(('14', '15', '16'))],
    (('14', '15'), '15'),
    (('15', '14'), '15'),
    (('14',), '14'),
    (('26.1', '14', '15', '16'), '16'),
    (('26.1',), '26.1'),
    ((), None),
])
@pytest.mark.parametrize('paginated', [False, True])
def test_ios_priority(versions, expected, paginated):
    catalogue = [{'type': 'IOS', 'name': f'iOS {v}', 'os_version': v} for v in versions]
    payload = {'items': catalogue} if paginated else catalogue
    assert resolve_ms_os_version(payload, OS_IOS) == expected
