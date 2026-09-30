"""Validate downloaded APKs and report native ABIs without extracting archives."""
import shutil
import logging
import os
import re
from mdast_cli.helpers.file_utils import cleanup_file
import tempfile
import zipfile
import zlib
from pathlib import Path


logger = logging.getLogger(__name__)

def _inspect_apk(source):
    with zipfile.ZipFile(source) as apk:
        if 'AndroidManifest.xml' not in apk.namelist() or apk.testzip() is not None:
            raise ValueError('APK has no AndroidManifest.xml or has a CRC error')
        return {name.split('/')[1] for name in apk.namelist()
                if name.startswith('lib/') and len(name.split('/')) == 3 and name.endswith('.so')}


def inspect_apk_artifact(path):
    """Return verified APK count and native ABIs; reject empty/malformed containers."""
    path = Path(path)
    try:
        if path.suffix == '.apk':
            return {'apk_count': 1, 'abis': sorted(_inspect_apk(path))}
        with zipfile.ZipFile(path) as bundle:
            entries = [item for item in bundle.infolist() if item.filename.endswith('.apk') and not item.is_dir()]
            if not entries:
                raise ValueError('archive contains no APK files')
            if bundle.testzip() is not None:
                raise ValueError('archive has a CRC error')
            abis = set()
            for entry in entries:
                with bundle.open(entry) as source, tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024) as apk:
                    shutil.copyfileobj(source, apk)
                    apk.seek(0)
                    abis.update(_inspect_apk(apk))
            return {'apk_count': len(entries), 'abis': sorted(abis)}
    except (ValueError, OSError, RuntimeError, zipfile.BadZipFile, zlib.error, EOFError) as error:
        raise RuntimeError(f'Google Play: invalid downloaded APK artifact: {error}') from error


def _local_artifact(path: Path, root: Path) -> bool:
    """Only accept regular artifacts owned by this download job."""
    try:
        path.absolute().relative_to(root)
        path.resolve().relative_to(root)
    except (ValueError, OSError, RuntimeError):
        return False
    return not any(item.is_symlink() for item in (path, *path.parents) if item != root and root in item.parents)


def _pack_splits(directory: Path, root: Path, package_name: str) -> str | None:
    members = []
    for current, dirs, files in os.walk(directory, followlinks=False):
        dirs[:] = sorted(d for d in dirs if _local_artifact(Path(current) / d, root))
        for name in sorted(files):
            path = Path(current) / name
            if not _local_artifact(path, root):
                continue
            members.append(path)
    apks = [path for path in members if path.suffix.lower() == '.apk']
    if not apks or not all(zipfile.is_zipfile(path) for path in apks):
        return None
    archive = root / f'{package_name}.zip'
    try:
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as target:
            for path in members:
                relative = path.relative_to(directory).as_posix()
                if relative == f'{package_name}.apk':
                    relative = 'base-master.apk'
                    if directory.joinpath(relative).exists():
                        raise RuntimeError('Google Play: ambiguous base APK in split directory')
                target.write(path, arcname=relative)
    except BaseException:
        cleanup_file(str(archive))
        raise
    try:
        shutil.rmtree(directory)
    except OSError:
        logger.warning('gp:cleanup_split_dir_failed')
    return str(archive)


def _prepare_artifact(path: Path, root: Path, package_name: str) -> str | None:
    if not _local_artifact(path, root):
        return None
    if path.is_dir():
        if path.resolve() == root:
            return None
        return _pack_splits(path, root, package_name)
    if not path.is_file() or path.suffix.lower() not in {'.apk', '.apks', '.zip'}:
        return None
    if not zipfile.is_zipfile(path):
        return None
    if path.suffix.lower() == '.apk':
        return str(path)
    with zipfile.ZipFile(path) as archive:
        if not any(info.filename.lower().endswith('.apk') for info in archive.infolist()):
            return None
    if path.suffix.lower() == '.apks':
        # APKS already is a ZIP of split APKs. Rename it, never nest it inside a ZIP.
        destination = path.with_suffix('.apks.zip')
        os.replace(path, destination)
        return str(destination)
    return str(path)


def _find_artifact(download_dir: str, package_name: str, output: str) -> str | None:
    root = Path(download_dir).resolve()
    candidates = [root / package_name, root / f'{package_name}.apk']
    for match in re.findall(r'(?:"([^"\n]+\.(?:apk|apks|zip))"|(/[^\s"\']+\.(?:apk|apks|zip)))', output):
        reported = Path(next(part for part in match if part))
        candidates.append(reported if reported.is_absolute() else root / reported)
    # Only package-related names are accepted without an explicit apkeep output path.
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if _local_artifact(Path(current) / d, root))
        for name in sorted(dirs + files):
            if name == package_name or name.startswith((package_name + '.', package_name + '-', package_name + '_')):
                candidates.append(Path(current) / name)
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        artifact = _prepare_artifact(candidate, root, package_name)
        if artifact:
            return artifact
    return None
