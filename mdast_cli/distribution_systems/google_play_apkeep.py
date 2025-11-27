import asyncio
import logging
import os
import shutil
import zipfile
import argparse
import sys
from typing import Final, Optional, List, Mapping
import re

from mdast_cli.helpers.logging_utils import redact
from mdast_cli.helpers.platform_utils import get_apkeep_binary_path

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SEC: Final[int] = 300
DEFAULT_DOWNLOAD_DIR: Final[str] = 'downloaded_apps'
DEFAULT_LOG_LEVEL: Final[str] = 'INFO'


async def fetch_aas_token(email: str, oauth2_token: str, timeout_sec: int) -> str:
    apkeep_path = get_apkeep_binary_path()
    logger.debug(f'Google Play - using apkeep binary: {apkeep_path}')

    redacted_email: Optional[Mapping[str, object]] = redact({'email': email})
    logger.info(f'Google Play - fetching AAS token via OAuth2 for account {(redacted_email or {}).get("email")}')
    proc = await asyncio.create_subprocess_exec(
        apkeep_path,
        '-e', email,
        '--oauth-token', oauth2_token,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        proc.kill()
        logger.error('gp:token_fetch_timeout')
        raise RuntimeError('Google Play: timeout while executing apkeep for token fetch')

    output = (stdout_b or b'').decode(errors='ignore') + '\n' + (stderr_b or b'').decode(errors='ignore')
    sanitized_output = []
    for line in output.splitlines():
        if line.strip().startswith('AAS Token: '):
            sanitized_output.append('AAS Token: ***')
        else:
            sanitized_output.append(line)
    sanitized_output_text = '\n'.join(sanitized_output)
    logger.debug(f'Google Play - apkeep output when fetching token (fragment): {sanitized_output_text[:1000]}')
    logger.debug(f'Google Play - full apkeep output when fetching token: {sanitized_output_text}')

    if proc.returncode != 0:
        raise RuntimeError(sanitized_output_text.strip() or 'Google Play: apkeep returned non-zero exit code')

    token_line = None
    for line in output.splitlines():
        if line.strip().startswith('AAS Token: '):
            token_line = line.strip()
            break
    if not token_line:
        raise RuntimeError(sanitized_output_text.strip() or 'Google Play: AAS token not found in apkeep output')
    parsed = token_line.split('AAS Token: ', 1)
    if len(parsed) != 2 or not parsed[1].strip():
        raise RuntimeError('Google Play: failed to parse AAS token from apkeep output')

    token_value = parsed[1].strip()
    logger.info('Google Play - AAS token successfully obtained')
    logger.debug(f'Google Play - AAS token (DEBUG): {token_value}')
    return token_value


async def download_app(
    download_dir: str,
    package_name: str,
    email: str,
    aas_token: str,
    timeout_sec: int,
) -> str:
    apkeep_path = get_apkeep_binary_path()
    logger.debug(f'Google Play - using apkeep binary: {apkeep_path} (package: {package_name})')

    proc = await asyncio.create_subprocess_exec(
        apkeep_path,
        '-a', package_name,
        '-d', 'google-play',
        '-e', email,
        '-o', 'split_apk=true,locale=ru_RU',
        '-t', aas_token,
        download_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        proc.kill()
        logger.error(f'Google Play - download timeout exceeded, package: {package_name}')
        raise RuntimeError('Google Play: timeout while executing apkeep for download')

    output = (stdout_b or b'').decode(errors='ignore') + '\n' + (stderr_b or b'').decode(errors='ignore')
    sanitized_output = []
    for line in output.splitlines():
        if line.strip().startswith('AAS Token: '):
            sanitized_output.append('AAS Token: ***')
        else:
            sanitized_output.append(line)
    sanitized_output_text = '\n'.join(sanitized_output)
    logger.debug(f'Google Play - apkeep output during download (fragment): {sanitized_output_text[:1000]} (package: {package_name})')
    logger.debug(f'Google Play - full apkeep output during download (package: {package_name}): {sanitized_output_text}')

    if proc.returncode != 0:
        raise RuntimeError(sanitized_output_text.strip() or 'apkeep returned non-zero exit code')

    if f'{package_name} downloaded successfully!' not in output:
        logger.warning(f'Google Play - success marker not found in output, continuing artifact check (package: {package_name})')

    split_dir = os.path.join(download_dir, package_name)
    single_apk = os.path.join(download_dir, f'{package_name}.apk')
    if os.path.isdir(split_dir):
        # Rename main APK to base-master.apk before zipping
        original_base_apk = os.path.join(split_dir, f'{package_name}.apk')
        renamed_base_apk = os.path.join(split_dir, 'base-master.apk')
        try:
            if os.path.exists(original_base_apk):
                if os.path.exists(renamed_base_apk):
                    try:
                        os.remove(renamed_base_apk)
                    except Exception:
                        pass
                os.replace(original_base_apk, renamed_base_apk)
                logger.info(f'Google Play - renamed base APK: {original_base_apk} → {renamed_base_apk} (package: {package_name})')
        except Exception as ex:
            logger.warning(f'Google Play - failed to rename base APK: {ex} (package: {package_name})')

        zip_base = os.path.join(download_dir, f'{package_name}')
        try:
            archive_path = shutil.make_archive(zip_base, 'zip', split_dir)
            logger.info(f'Google Play - artifact ready: {archive_path} (package: {package_name})')
            try:
                shutil.rmtree(split_dir)
                logger.debug(f'Google Play - temporary split directory removed: {split_dir} (package: {package_name})')
            except Exception as ex:
                logger.warning('gp:cleanup_split_dir_failed', extra={'package': package_name, 'dir': split_dir, 'error': str(ex)})
            return archive_path
        except Exception as ex:
            logger.error(f'Google Play - failed to archive split APKs: {ex} (package: {package_name})')
            raise RuntimeError(f'Google Play: failed to archive split APKs: {ex}')
    if os.path.isfile(single_apk):
        # Keep single APK as the final artifact (no zipping)
        logger.info(f'Google Play - artifact ready: {single_apk} (package: {package_name})')
        return single_apk

    # Try to infer artifact path(s) from apkeep output (absolute .apk/.apks paths)
    candidate_paths = set()
    try:
        for match in re.findall(r'(/[^ \n"]+\.(?:apks?|zip))', output):
            candidate_paths.add(match)
    except Exception:
        pass
    if candidate_paths:
        logger.debug(f'Google Play - candidates from apkeep output: {list(candidate_paths)[:10]} (package: {package_name})')
        for path in candidate_paths:
            if os.path.isdir(path):
                # Directory with splits; zip it
                original_base_apk = os.path.join(path, f'{package_name}.apk')
                renamed_base_apk = os.path.join(path, 'base-master.apk')
                try:
                    if os.path.exists(original_base_apk):
                        if os.path.exists(renamed_base_apk):
                            try:
                                os.remove(renamed_base_apk)
                            except Exception:
                                pass
                        os.replace(original_base_apk, renamed_base_apk)
                        logger.info(f'Google Play - renamed base APK: {original_base_apk} → {renamed_base_apk} (package: {package_name})')
                except Exception as ex:
                    logger.warning(f'Google Play - failed to rename base APK: {ex} (package: {package_name})')
                try:
                    archive_path = shutil.make_archive(path, 'zip', path)
                    logger.info(f'Google Play - artifact ready: {archive_path} (package: {package_name})')
                    try:
                        shutil.rmtree(path)
                        logger.debug(f'Google Play - temporary split directory removed: {path} (package: {package_name})')
                    except Exception as ex:
                        logger.warning('gp:cleanup_split_dir_failed', extra={'package': package_name, 'dir': path, 'error': str(ex)})
                    return archive_path
                except Exception as ex:
                    logger.error(f'Google Play - failed to archive split APKs: {ex} (package: {package_name})')
            elif os.path.isfile(path):
                # If apkeep produced an .apks file, repackage to .zip and remove source
                if path.endswith('.apks'):
                    zip_path = os.path.splitext(path)[0] + '.zip'
                    try:
                        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                            zf.write(path, arcname=os.path.basename(path))
                        logger.info(f'Google Play - artifact ready: {zip_path} (package: {package_name})')
                        try:
                            os.remove(path)
                            logger.debug(f'Google Play - temporary .apks removed: {path} (package: {package_name})')
                        except Exception as ex:
                            logger.debug(f'Google Play - failed to remove temporary .apks: {path}, error: {ex} (package: {package_name})')
                        return zip_path
                    except Exception as ex:
                        logger.error(f'Google Play - failed to repackage .apks to .zip: {ex} (package: {package_name})')
                elif path.endswith('.apk'):
                    # Keep single APK as the final artifact
                    logger.info(f'Google Play - artifact ready: {path} (package: {package_name})')
                    return path
                elif path.endswith('.zip'):
                    logger.info(f'Google Play - artifact ready: {path} (package: {package_name})')
                    return path

    # Fallback: scan download_dir for recent files/dirs matching the package
    try:
        candidates = []
        for root, dirs, files in os.walk(download_dir):
            for f in files:
                if f.startswith(package_name) and (f.endswith('.apk') or f.endswith('.apks') or f.endswith('.zip')):
                    candidates.append(os.path.join(root, f))
            for d in dirs:
                if d.startswith(package_name):
                    candidates.append(os.path.join(root, d))
        if candidates:
            logger.debug(f'Google Play - found candidates: {candidates[:10]} (package: {package_name})')
            # Prefer .apks/.zip, then split dir, then .apk
            for ext in ('.zip',):
                for c in candidates:
                    if c.endswith(ext) and os.path.isfile(c):
                        logger.info('gp:artifact_ready', extra={'package': package_name, 'artifact': c})
                        return c
            # Repack .apks files to .zip
            for c in candidates:
                if c.endswith('.apks') and os.path.isfile(c):
                    zip_path = os.path.splitext(c)[0] + '.zip'
                    try:
                        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                            zf.write(c, arcname=os.path.basename(c))
                        logger.info(f'Google Play - artifact ready: {zip_path} (package: {package_name})')
                        try:
                            os.remove(c)
                            logger.debug(f'Google Play - temporary .apks removed: {c} (package: {package_name})')
                        except Exception as ex:
                            logger.debug(f'Google Play - failed to remove temporary .apks: {c}, error: {ex} (package: {package_name})')
                        return zip_path
                    except Exception as ex:
                        logger.error('gp:repack_apks_failed', extra={'package': package_name, 'error': str(ex)})
            # split dir
            for c in candidates:
                if os.path.isdir(c):
                    original_base_apk = os.path.join(c, f'{package_name}.apk')
                    renamed_base_apk = os.path.join(c, 'base-master.apk')
                    try:
                        if os.path.exists(original_base_apk):
                            if os.path.exists(renamed_base_apk):
                                try:
                                    os.remove(renamed_base_apk)
                                except Exception:
                                    pass
                            os.replace(original_base_apk, renamed_base_apk)
                            logger.info('gp:rename_base_apk', extra={'package': package_name, 'from': original_base_apk, 'to': renamed_base_apk})
                    except Exception as ex:
                        logger.warning('gp:rename_base_apk_failed', extra={'package': package_name, 'error': str(ex)})
                    try:
                        archive_path = shutil.make_archive(c, 'zip', c)
                        logger.info(f'Google Play - artifact ready: {archive_path} (package: {package_name})')
                        try:
                            shutil.rmtree(c)
                            logger.debug(f'Google Play - temporary split directory removed: {c} (package: {package_name})')
                        except Exception as ex:
                            logger.debug(f'Google Play - failed to remove temporary split directory: {c}, error: {ex} (package: {package_name})')
                        return archive_path
                    except Exception as ex:
                        logger.error(f'Google Play - failed to archive split APKs: {ex} (package: {package_name})')
            # single apk (keep as-is)
            for c in candidates:
                if c.endswith('.apk') and os.path.isfile(c):
                    logger.info(f'Google Play - artifact ready: {c} (package: {package_name})')
                    return c
    except Exception as ex:
        logger.debug(f'Google Play - failed to scan directory for candidates: {ex} (package: {package_name})')

    logger.error(f'Google Play - artifact not found after successful download (package: {package_name})')
    raise RuntimeError('Google Play: download reports success but artifact not found')


def _ensure_dir_exists(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as ex:
        logger.error('gp:mkdir_failed', extra={'dir': path, 'error': str(ex)})
        raise


def _configure_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        stream=sys.stdout,
    )
    logger.debug(f'Google Play - logging configured (level: {level})')


async def _run_cli(
    email: str,
    package_name: str,
    oauth2_token: Optional[str],
    aas_token: Optional[str],
) -> int:
    red_email: Optional[Mapping[str, object]] = redact({'email': email})
    logger.info(f'Google Play - start: package {package_name}, email {(red_email or {}).get("email")}, '
                f'OAuth2={bool(oauth2_token)}, AAS={bool(aas_token)}, download directory "{DEFAULT_DOWNLOAD_DIR}"')
    _ensure_dir_exists(DEFAULT_DOWNLOAD_DIR)

    try:
        token_to_use = aas_token
        if not token_to_use:
            logger.info(f'Google Play - AAS token not provided, will be fetched via OAuth2 (package: {package_name})')
            token_to_use = await fetch_aas_token(email=email, oauth2_token=oauth2_token or '', timeout_sec=DEFAULT_TIMEOUT_SEC)
            logger.info(f'Google Play - AAS token obtained (package: {package_name})')
        else:
            logger.debug(f'Google Play - AAS token (DEBUG): {token_to_use}')

        artifact = await download_app(
            download_dir=DEFAULT_DOWNLOAD_DIR,
            package_name=package_name,
            email=email,
            aas_token=token_to_use or '',
            timeout_sec=DEFAULT_TIMEOUT_SEC,
        )
        logger.info(f'Google Play - success: artifact {artifact} (package: {package_name})')
        return 0
    except Exception as ex:
        logger.exception(f'Google Play - error: {ex} (package: {package_name})')
        return 1


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Google Play downloader (apkeep-based)')
    parser.add_argument('--email', required=True, help='Google account email')
    parser.add_argument('--package', required=True, help='Android package name')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--oauth2-token', help='OAuth2 token to fetch AAS token')
    group.add_argument('--aas-token', help='Already obtained AAS token; skips fetch')
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    _configure_logging(DEFAULT_LOG_LEVEL)

    if not args.aas_token and not args.oauth2_token:
        logger.error('gp:args_missing_token')
        return 2

    try:
        exit_code = asyncio.run(
            _run_cli(
                email=args.email,
                package_name=args.package,
                oauth2_token=args.oauth2_token,
                aas_token=args.aas_token,
            )
        )
        return exit_code
    except KeyboardInterrupt:
        logger.warning('gp:cli_interrupted')
        return 130


if __name__ == '__main__':
    sys.exit(main())


