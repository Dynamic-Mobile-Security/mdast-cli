"""The native build must reject unverified dependency overrides."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    'sap_build', Path(__file__).resolve().parents[1] / 'tools/sap/build.py')
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)
PIN = {
    'module': 'example.test/compress', 'from_version': 'v1.0.0',
    'version': 'v1.0.1', 'sum': 'h1:verified-source', 'go_mod_sum': 'h1:verified-mod',
}


@pytest.fixture
def source(tmp_path):
    (tmp_path / 'go.mod').write_text('module test\n\nrequire (\n\texample.test/compress v1.0.0\n)\n')
    (tmp_path / 'go.sum').write_text('other.test/module v1.2.3 h1:unchanged\n')
    return tmp_path


def test_verified_dependency_is_selected_without_changing_unrelated_sums(source):
    with patch.object(build.subprocess, 'check_output', return_value=json.dumps({
        'Sum': PIN['sum'], 'GoModSum': PIN['go_mod_sum'],
    })):
        build.configure_dependencies(source, 'go', [PIN])
    assert 'example.test/compress v1.0.1\n' in (source / 'go.mod').read_text()
    assert set((source / 'go.sum').read_text().splitlines()) == {
        'other.test/module v1.2.3 h1:unchanged',
        'example.test/compress v1.0.1 h1:verified-source',
        'example.test/compress v1.0.1/go.mod h1:verified-mod',
    }


@pytest.mark.parametrize('reply', [
    {'Sum': 'wrong', 'GoModSum': PIN['go_mod_sum']},
    {'Sum': PIN['sum'], 'GoModSum': 'wrong'},
    {'Sum': PIN['sum'], 'GoModSum': PIN['go_mod_sum'], 'Error': 'download failed'},
])
def test_unverified_dependency_does_not_modify_sources(source, reply):
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    with patch.object(build.subprocess, 'check_output', return_value=json.dumps(reply)):
        with pytest.raises(SystemExit, match='checksum verification failed'):
            build.configure_dependencies(source, 'go', [PIN])
    assert {p.name: p.read_bytes() for p in source.iterdir()} == before


def test_changed_upstream_dependency_is_rejected(source):
    (source / 'go.mod').write_text('module test\nrequire example.test/compress v2.0.0\n')
    with patch.object(build.subprocess, 'check_output', return_value=json.dumps({
        'Sum': PIN['sum'], 'GoModSum': PIN['go_mod_sum'],
    })):
        with pytest.raises(SystemExit, match='no longer matches upstream'):
            build.configure_dependencies(source, 'go', [PIN])


def test_conflicting_checksum_is_rejected(source):
    (source / 'go.sum').write_text('example.test/compress v1.0.1 h1:untrusted\n')
    with patch.object(build.subprocess, 'check_output', return_value=json.dumps({
        'Sum': PIN['sum'], 'GoModSum': PIN['go_mod_sum'],
    })):
        with pytest.raises(SystemExit, match='Conflicting SAP dependency checksum'):
            build.configure_dependencies(source, 'go', [PIN])


def test_go_toolchain_matches_every_build_path():
    """Docker must not silently rebuild the release helper with an older Go."""
    import re

    root = Path(__file__).resolve().parents[1]
    patterns = {
        'Dockerfile': r'^FROM golang:([0-9.]+)-bookworm AS go-toolchain$',
        '.github/workflows/python-publish.yml': r"go-version: '([0-9.]+)'",
        '.github/workflows/tests.yml': r"go-version: '([0-9.]+)'",
        'README.md': r'install Go ([0-9.]+) and run',
    }
    versions = {}
    for name, pattern in patterns.items():
        found = re.findall(pattern, (root / name).read_text(), re.MULTILINE)
        assert len(found) == 1, f'Expected one explicit Go toolchain in {name}'
        versions[name] = found[0]
    assert len(set(versions.values())) == 1, versions
    version = versions['.github/workflows/python-publish.yml']
    assert tuple(int(part) for part in version.split('.')) >= (1, 27, 3)
