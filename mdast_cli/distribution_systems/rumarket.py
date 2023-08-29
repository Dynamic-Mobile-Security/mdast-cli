import logging
import os

import requests

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
    r = requests.get(app_info['download_url'])
    if r.status_code == 401:
        raise RuntimeError(f'Rumarket - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    file_path = f"{download_path}/{app_info['package_name']}-{app_info['version_name']}.apk"

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Rumarket - Creating directory {download_path} for downloading app from Rumarket')

    f = open(file_path, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()
    logger.info(f'Rumarket - Apk was downloaded from rumarket to {file_path}')

    return file_path
