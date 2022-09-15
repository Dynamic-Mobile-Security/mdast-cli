import logging
import os

import requests

logger = logging.getLogger(__name__)


def get_app_info(package_name):
    app_info = requests.get(f'https://backapi.rustore.ru/applicationData/overallInfo/{package_name}')
    if app_info.status_code == 200:
        body_info = app_info.json()['body']
        logger.info(f"Rustore - Successfully found app with package name: {package_name},"
                    f" version:{body_info['versionName']}, company: {body_info['companyName']}")
    apk_uid = body_info['apkUid']
    return {
        'package_name': body_info['packageName'],
        'version': body_info['versionName'],
        'download_url': f'https://static.rustore.ru/{apk_uid}',
        'integration_type': 'rustore'
    }


def rustore_download_app(package_name, download_path):
    app_info = get_app_info(package_name)
    logger.info('Rustore - Start downloading application')
    r = requests.get(app_info['download_url'])
    if r.status_code == 401:
        raise RuntimeError(f'Rustore - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    file_path = f"{download_path}/{app_info['package_name']}-{app_info['version']}.apk"

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
