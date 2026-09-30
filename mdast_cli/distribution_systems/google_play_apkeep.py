import asyncio
import logging
import os
import argparse
import sys
from typing import Final, Optional, Mapping
import re
import tempfile
from pathlib import Path

from mdast_cli.helpers.apk_artifacts import inspect_apk_artifact, _find_artifact

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
    sanitized_output_text = _safe_output('\n'.join(sanitized_output), email, oauth2_token)
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
    return token_value


def _safe_output(output: str, *secrets: str) -> str:
    for secret in sorted((value for value in secrets if value), key=len, reverse=True):
        output = output.replace(secret, '[redacted]')
    output = re.sub(r'https?://\S+', '[url]', output)
    return output[-3000:]


async def download_app(
    download_dir: str,
    package_name: str,
    email: str,
    aas_token: str,
    timeout_sec: int,
) -> str:
    if not re.fullmatch(r'[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+', package_name):
        raise RuntimeError('Google Play: invalid package name')
    apkeep_path = get_apkeep_binary_path()
    directory = Path(download_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout_sec
    for device in ('sting_x86_64', 'px_9a'):
        logger.info('Google Play: запрос профиля %s', device)
        with tempfile.TemporaryDirectory(prefix='.google-play-', dir=directory) as work:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise RuntimeError('Google Play: download timeout exceeded')
            proc = await asyncio.create_subprocess_exec(
                apkeep_path, '-a', package_name, '-d', 'google-play', '-e', email,
                '-o', f'split_apk=true,locale=ru_RU,device={device}', '-t', aas_token, work,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=remaining)
            except asyncio.TimeoutError as error:
                if proc.returncode is None:
                    proc.kill()
                await proc.wait()
                raise RuntimeError('Google Play: download timeout exceeded') from error
            except asyncio.CancelledError:
                if proc.returncode is None:
                    proc.kill()
                await proc.wait()
                raise
            output = (stdout or b'').decode(errors='replace') + '\n' + (stderr or b'').decode(errors='replace')
            unavailable = 'STING_APP_UNAVAILABLE:' in output
            if proc.returncode != 0:
                if proc.returncode == 3 and unavailable and device == 'sting_x86_64':
                    logger.warning('Google Play: приложение недоступно профилю x86_64; пробую ARM fallback')
                    continue
                raise RuntimeError('Google Play: apkeep failed: ' + _safe_output(output, email, aas_token))
            found = _find_artifact(work, package_name, output)
            if found is None:
                raise RuntimeError('Google Play: apkeep produced no valid APK artifact')
            artifact = Path(found)
            info = inspect_apk_artifact(artifact)
            abis = info['abis']
            if not abis:
                logger.info('Google Play: APK без native libraries, не зависит от ABI')
            elif 'x86_64' in abis:
                logger.info('Google Play: получена сборка x86_64; ABI=%s', ','.join(abis))
            elif set(abis) & {'arm64-v8a', 'armeabi-v7a', 'armeabi'}:
                logger.warning('Google Play: ARM fallback, x86_64 в выдаче отсутствует; ABI=%s', ','.join(abis))
            else:
                raise RuntimeError('Google Play: unsupported native ABIs: ' + ','.join(abis))
            target = directory / artifact.name
            os.replace(artifact, target)
            logger.info('Google Play: проверено APK=%s, ABI=%s', info['apk_count'], ','.join(abis) or 'universal')
            return str(target)
    raise RuntimeError('Google Play: app is unavailable for x86_64 and ARM profiles')


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


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Google Play downloader (apkeep-based)')
    parser.add_argument('--email', required=True, help='Google account email')
    parser.add_argument('--package', required=True, help='Android package name')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--oauth2-token', help='OAuth2 token to fetch AAS token')
    group.add_argument('--aas-token', help='Already obtained AAS token; skips fetch')
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
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

