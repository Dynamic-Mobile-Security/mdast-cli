#!/usr/bin/env python3
"""Reject a wheel missing a release SAP helper or its executable mode."""
import hashlib
from pathlib import Path
import zipfile

from build import ROOT, TARGETS

prefix = 'mdast_cli/distribution_systems/appstore_client/'
wheels = list((ROOT / 'dist').glob('*.whl'))
assert len(wheels) == 1, 'Expected exactly one release wheel'
with zipfile.ZipFile(wheels[0]) as wheel:
    for target in TARGETS:
        name = prefix + 'bin/mdast-sap-' + target + ('.exe' if target.startswith('windows') else '')
        member = wheel.getinfo(name)
        assert member.external_attr >> 16 & 0o111, 'SAP helper is not executable'
        assert hashlib.sha256(wheel.read(name)).digest() == hashlib.sha256((ROOT / name).read_bytes()).digest()
    assert wheel.read(prefix + 'IPATOOL-LICENSE')
print('Verified all six SAP helpers and upstream license in', wheels[0].name)
