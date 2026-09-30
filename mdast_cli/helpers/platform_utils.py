"""Platform detection and binary path utilities."""
import os
import hashlib
import json
import subprocess
import platform
from pathlib import Path


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == 'Darwin'


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == 'Linux'


def get_apkeep_binary_path() -> str:
    """Use the verified bundled Стинг build; never silently select an old PATH binary."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    machine = {'aarch64': 'arm64', 'amd64': 'x86_64'}.get(machine, machine)
    name = f'apkeep-{system}-{machine}'
    directory = Path(__file__).resolve().parent.parent / 'bin'
    manifest_path = directory / 'apkeep-manifest.json'
    if not manifest_path.is_file():
        raise RuntimeError('Google Play: bundled apkeep manifest is missing; reinstall mdast-cli')
    manifest = json.loads(manifest_path.read_text())
    binary = directory / name
    expected = manifest['binaries'].get(name)
    if not expected or not binary.is_file():
        raise RuntimeError(f'Google Play: bundled apkeep is unavailable for {system}/{machine}')
    if hashlib.sha256(binary.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Google Play: bundled apkeep checksum mismatch; reinstall mdast-cli')
    if not os.access(binary, os.X_OK):
        binary.chmod(binary.stat().st_mode | 0o111)
    try:
        result = subprocess.run([str(binary), '--version'], capture_output=True, text=True, timeout=10, check=True)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError('Google Play: cannot execute bundled apkeep on this host') from error
    if result.stdout.strip() != 'apkeep ' + manifest['version']:
        raise RuntimeError('Google Play: bundled apkeep version mismatch; reinstall mdast-cli')
    return str(binary)
