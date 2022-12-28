import logging
import os

import requests

logger = logging.getLogger(__name__)


def get_app_info(package_name):
    req = requests.get(f'https://backapi.rustore.ru/applicationData/overallInfo/{package_name}')
    if req.status_code == 200:
        body_info = req.json()['body']
        logger.info(f"Rustore - Successfully found app with package name: {package_name},"
                    f" version:{body_info['versionName']}, company: {body_info['companyName']}")
    else:
        raise RuntimeError(f'Rustore - Failed to get application info. Request return status code: {req.status_code}')

    apk_uid = body_info['apkUid']
    return {
        'integration_type': 'rustore',
        'download_url': f'https://static.rustore.ru/{apk_uid}',
        'package_name': body_info['packageName'],
        'version_name': body_info['versionName'],
        'version_code': body_info['versionCode'],
        'min_sdk_version': body_info['minSdkVersion'],
        'max_sdk_version': body_info['maxSdkVersion'],
        'target_sdk_version': body_info['targetSdkVersion'],
        'file_size': body_info['fileSize'],
        'icon_url': body_info['iconUrl']
    }


def rustore_download_app(package_name, download_path):
    app_info = get_app_info(package_name)
    logger.info('Rustore - Start downloading application')
    r = requests.get(app_info['download_url'])
    if r.status_code == 401:
        raise RuntimeError(f'Rustore - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    file_path = f"{download_path}/{app_info['package_name']}-{app_info['version_name']}.apk"

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Rustore - Creating directory {download_path} for downloading app from Rustore')

    f = open(file_path, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()
    logger.info(f'Rustore - Apk was downloaded from rustore to {file_path}')

    return file_path
