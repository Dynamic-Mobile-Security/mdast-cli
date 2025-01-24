import logging
import os
import zipfile

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

    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        'appId': body_info['appId'],
        'firstInstall': True
    }
    download_link_resp = requests.post('https://backapi.rustore.ru/applicationData/download-link',
                                       headers=headers, json=body)
    if req.status_code == 200:
        download_link = download_link_resp.json()['body']['apkUrl']
    else:
        raise RuntimeError(f'Rustore - Failed to get application download link.'
                           f' Request return status code: {req.status_code}')

    return {
        'integration_type': 'rustore',
        'download_url': download_link,
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

    if app_info['download_url'].endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            first_file = file_list[0]
            with zip_ref.open(first_file) as source_file:
                os.remove(file_path)
                with open(file_path, 'wb') as target_file:
                    target_file.write(source_file.read())

    logger.info(f'Rustore - Apk was downloaded from rustore to {file_path}')

    return file_path
