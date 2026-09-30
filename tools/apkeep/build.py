#!/usr/bin/env python3
"""Prepare pinned apkeep sources and build the Стинг x86_64-preferred profile."""
import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((Path(__file__).with_name('upstream.json')).read_text())

def fetch(name, directory):
    item = META[name]
    url = f'https://static.crates.io/crates/{name}/{name}-{item["version"]}.crate'
    with urllib.request.urlopen(url, timeout=90) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise RuntimeError(f'{name}: upstream checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        archive.extractall(directory, filter='data')
    return directory / f'{name}-{item["version"]}'

def prepare(directory):
    directory.mkdir(parents=True, exist_ok=True)
    app = fetch('apkeep', directory)
    gp = fetch('gpapi', directory)
    props = (gp / 'device.properties').read_text()
    match = re.search(r'(?ms)^\[px_9a\]\n(.*?)(?=^\[|\Z)', props)
    if not match:
        raise RuntimeError('Pinned upstream has no px_9a profile')
    profile, count = re.subn(r'(?m)^Platforms=.*$', f'Platforms={META["platforms"]}', match[1])
    if count != 1:
        raise RuntimeError('Pinned upstream Platforms field changed')
    identity = re.search(r'(?ms)^\[google_kiwi_x86_64\]\n(.*?)(?=^\[|\Z)', props)
    if not identity:
        raise RuntimeError('Pinned upstream has no x86_64 device identity')
    # Google selects ARM for the Pixel identity even with native_platform=x86_64.
    # Keep phone capabilities, but identify the actual requested x86_64 hardware.
    for key in META['identity_fields']:
        value = re.search(r'(?m)^' + re.escape(key) + r'=(.*)$', identity[1])
        if not value:
            raise RuntimeError(f'Missing upstream identity field: {key}')
        profile, count = re.subn(r'(?m)^' + re.escape(key) + r'=.*$',
                                lambda _: key + '=' + value[1], profile)
        if count != 1:
            raise RuntimeError(f'Missing base identity field: {key}')
    (gp / 'device.properties').write_text(props + f'\n[{META["profile"]}]\n' + profile)
    (gp / 'src/device_properties.bin').unlink(missing_ok=True)
    rust = app / 'src/download_sources/google_play.rs'
    text = rust.read_text()
    if text.count('unwrap_or("px_9a")') != 2:
        raise RuntimeError('Pinned upstream Google Play default changed')
    text = text.replace('unwrap_or("px_9a")', f'unwrap_or("{META["profile"]}")')
    # indicatif hides println diagnostics when captured by a non-TTY caller.
    # Preserve a machine-readable availability error for the bounded ARM fallback.
    text = text.replace('use std::collections::HashMap;', 'use std::collections::HashMap;\nuse std::cell::Cell;')
    text = text.replace('    let mp = Rc::new(MultiProgress::new());', '    let failed = Rc::new(Cell::new(false));\n    let mp = Rc::new(MultiProgress::new());')
    text = text.replace('            let mp_log = Rc::clone(&mp);', '            let mp_log = Rc::clone(&mp);\n            let failed = Rc::clone(&failed);')
    text, count = re.subn(r'mp_log\.println\(format!\(([^\n]+)\)\)\.unwrap\(\);', r'eprintln!(\1);', text)
    if count != 8:
        raise RuntimeError(f'Pinned upstream error diagnostics changed: {count}')
    text = text.replace('eprintln!("Invalid app response for {}. Skipping...", app_id);', 'eprintln!("STING_APP_UNAVAILABLE: {}", app_id);')
    for marker in ('File already exists', 'Split APK directory already exists', 'STING_APP_UNAVAILABLE', 'Permission denied', 'An error has occurred attempting to download {}. Skipping', 'Specific versions can not'):
        text = re.sub(r'(\s*)(eprintln!\("' + re.escape(marker) + ')', r'\1failed.set(true);\1\2', text)
    text = text.replace('    ).buffer_unordered(parallel).collect::<Vec<()>>().await;', '    ).buffer_unordered(parallel).collect::<Vec<()>>().await;\n    if failed.get() { std::process::exit(3); }')
    download, token = text.split('pub async fn request_aas_token', 1)
    download = download.replace('Err(_) => {', 'Err(error) => {\n                            let message = format!("{:?}", error);\n                            let redacted = regex::Regex::new(r"https?://\\S+").unwrap().replace_all(&message, "[url]");\n                            eprintln!("STING_DOWNLOAD_ERROR: {}", redacted);')
    text = download + 'pub async fn request_aas_token' + token
    rust.write_text(text)
    cargo = app / 'Cargo.toml'
    text = cargo.read_text().replace('version = "1.0.0"', f'version = "{META["patched_version"]}"', 1)
    text += f'\n[patch.crates-io]\ngpapi = {{ path = "../{gp.name}" }}\n'
    cargo.write_text(text)
    lock = app / 'Cargo.lock'
    text = lock.read_text().replace('name = "apkeep"\nversion = "1.0.0"', f'name = "apkeep"\nversion = "{META["patched_version"]}"', 1)
    text, count = re.subn(r'(name = "gpapi"\nversion = "6.1.0"\n)source = [^\n]+\nchecksum = [^\n]+\n', r'\1', text)
    if count != 1:
        raise RuntimeError('Pinned upstream lockfile changed')
    lock.write_text(text)
    shutil.copy2(app / 'LICENSE', ROOT / 'mdast_cli/bin/APKEEP-LICENSE')
    shutil.copy2(gp / 'LICENSE', ROOT / 'mdast_cli/bin/GPAPI-LICENSE')
    return app

def install(binary, name):
    out = ROOT / 'mdast_cli/bin' / name
    shutil.copy2(binary, out)
    out.chmod(0o755)
    manifest = ROOT / 'mdast_cli/bin/apkeep-manifest.json'
    data = json.loads(manifest.read_text()) if manifest.exists() else {'version': META['patched_version'], 'profile': META['profile'], 'platforms': META['platforms'].split(','), 'binaries': {}}
    data.update(version=META['patched_version'], profile=META['profile'], platforms=META['platforms'].split(','))
    data['binaries'][name] = hashlib.sha256(out.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    print(out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--target')
    parser.add_argument('--name')
    parser.add_argument('--install', type=Path)
    args = parser.parse_args()
    if args.install:
        if not args.name: parser.error('--install requires --name')
        install(args.install, args.name)
    else:
        app = prepare(args.directory.resolve())
        print(app, flush=True)
        if not args.prepare_only:
            cmd = ['cargo', 'build', '--release', '--locked', '--manifest-path', str(app / 'Cargo.toml')]
            if args.target: cmd += ['--target', args.target]
            subprocess.run(cmd, check=True)
            if args.name:
                install(app / 'target' / (args.target or '') / 'release/apkeep', args.name)
