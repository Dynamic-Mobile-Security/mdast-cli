import logging
import os

import requests
from tqdm import tqdm

from mdast_cli.helpers.file_utils import ensure_download_dir, cleanup_file

logger = logging.getLogger(__name__)


def get_app_info(package_name):
    req = requests.get(f'https://store-api.ruplay.market/api/v1/app/getApp/{package_name}')
    if req.status_code == 200:
        app_info = req.json()['data']
        logger.info(f"Rumarket - Successfully found app with package name: {package_name},"
                    f" version:{app_info['latestApk']['versionName']}, company: {app_info['author']['name']}")
    else:
        raise RuntimeError(f'Rumarket - Failed to get application info. Request return status code: {req.status_code}')

    return {
        'integration_type': 'rumarket',
        'download_url': f"https://cdn.ruplay.market/data/apks/{app_info['latestApk']['name']}",
        'package_name': app_info['packageName'],
        'version_name': app_info['latestApk']['versionName'],
        'version_code': app_info['latestApk']['versionCode'],
        'min_sdk_version': app_info['latestApk']['minSdkVersion'],
        'target_sdk_version': app_info['latestApk']['targetSdkVersion'],
        'file_size': app_info['latestApk']['size'],
        'icon_url': app_info['iconUrl']
    }


def rumarket_download_app(package_name, download_path):
    app_info = get_app_info(package_name)
    logger.info(f'Rumarket - Start downloading application {package_name}')
    r = requests.get(app_info['download_url'], stream=True)
    if r.status_code == 401:
        raise RuntimeError(f'Rumarket - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    file_path = f"{download_path}/{app_info['package_name']}-{app_info['version_name']}.apk"

    ensure_download_dir(download_path)
    logger.info(f'Rumarket - Creating directory {download_path} for downloading app from Rumarket')

    try:
        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 512 * 1024
        with open(file_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                      desc=f"RuMarket - Downloading {package_name}",
                      disable=total_size == 0) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    except Exception as e:
        # Cleanup partial file on error
        cleanup_file(file_path)
        raise RuntimeError(f'Rumarket - Failed to write downloaded file: {e}')

    logger.info(f'Rumarket - Apk was downloaded from rumarket to {file_path}')

    return file_path
