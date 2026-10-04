#!/usr/bin/env python3
"""Build the SAP bridge from Go-checksum-verified, pinned ipatool sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ('linux-amd64', 'linux-arm64', 'darwin-amd64', 'darwin-arm64',
           'windows-amd64', 'windows-arm64')


def configure_runtime_cache(source):
    """Apply one guarded cache-location hook to verified upstream sources."""
    for name in ('internal/sap/assets/assets.go', 'internal/sap/unicorn/cache.go'):
        path = source / name
        content = path.read_text()
        if content.count('os.UserCacheDir()') != 1 or content.count('import (') != 1:
            raise SystemExit('Pinned SAP cache hook no longer matches upstream')
        content = content.replace('import (', 'import (\n\t"github.com/majd/ipatool/v2/internal/sap/cachepath"', 1)
        path.write_text(content.replace('os.UserCacheDir()', 'cachepath.Directory()'))
    directory = source / 'internal/sap/cachepath'
    directory.mkdir()
    for name in ('cache.go', 'cache_test.go'):
        shutil.copy2(ROOT / 'tools/sap' / name, directory / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--go', default='go')
    parser.add_argument('--target', choices=(*TARGETS, 'host', 'all'), default='host')
    args = parser.parse_args()
    pin = json.loads((ROOT / 'tools/sap/upstream.json').read_text())
    dependency = pin['module'] + '@' + pin['version']
    module = json.loads(subprocess.check_output([args.go, 'mod', 'download', '-json', dependency]))
    if module.get('Error') or module.get('Sum') != pin['sum']:
        raise SystemExit('Pinned ipatool source checksum verification failed')
    if args.target == 'host':
        goos, goarch = subprocess.check_output([args.go, 'env', 'GOOS', 'GOARCH'], text=True).split()
        targets = [goos + '-' + goarch]
    else:
        targets = TARGETS if args.target == 'all' else [args.target]
    out = ROOT / 'mdast_cli/distribution_systems/appstore_client/bin'
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mdast-sap-build-') as temporary:
        source = Path(temporary) / 'ipatool'
        shutil.copytree(module['Dir'], source)
        # Go module cache files are read-only; leave the cache untouched.
        for path in source.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        configure_runtime_cache(source)
        subprocess.run([args.go, 'test', '-mod=readonly', './internal/sap/cachepath'],
                       cwd=source, check=True)
        command = source / 'cmd/mdast-sap'
        command.mkdir()
        shutil.copy2(ROOT / 'tools/sap/main.go', command / 'main.go')
        for target in targets:
            goos, goarch = target.split('-')
            binary = out / ('mdast-sap-' + target + ('.exe' if goos == 'windows' else ''))
            env = dict(os.environ, GOOS=goos, GOARCH=goarch, CGO_ENABLED='0')
            subprocess.run([args.go, 'build', '-mod=readonly', '-trimpath', '-buildvcs=false',
                            '-ldflags=-s -w', '-o', str(binary), './cmd/mdast-sap'],
                           cwd=source, env=env, check=True)
            binary.chmod(0o755)
            print(json.dumps({'target': target, 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}), flush=True)
        shutil.copy2(source / 'LICENSE', ROOT / 'mdast_cli/distribution_systems/appstore_client/IPATOOL-LICENSE')


if __name__ == '__main__':
    main()
