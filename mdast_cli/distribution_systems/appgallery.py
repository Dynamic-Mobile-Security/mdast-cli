import logging
import os
import time

import requests

logger = logging.getLogger(__name__)


def get_app_info(app_id):
    get_interface_code_resp = requests.post('https://web-drru.hispace.dbankcloud.ru/webedge/getInterfaceCode')
    if get_interface_code_resp.status_code != 200:
        raise RuntimeError('Appgallery - Cannot get interface code, connection error')
    interface_code = get_interface_code_resp.json()
    timestamp = time.time()
    timestamp = str(timestamp).replace('.', '')
    headers = {
        'Interface-Code': f'{interface_code}_{timestamp}'
    }
    req = requests.get(f'https://web-drru.hispace.dbankcloud.ru/uowap/index?'
                       f'method=internal.getTabDetail&uri=app%7C{app_id}', headers=headers)
    if req.status_code == 200:
        resp_info = req.json()
    else:
        raise RuntimeError(f'Appgallery - Failed to get application info. '
                           f'Request return status code: {req.status_code}')
    app_info = {}

    layout_data = resp_info.get('layoutData', [])
    for element in layout_data:
        if 'dataList' not in element.keys():
            continue

        for item in element.get('dataList', []):
            if 'package' not in item.keys():
                continue
            if app_id != item.get('appid'):
                continue

            app_info['integration_type'] = 'appgallery'
            app_info['icon_url'] = item.get('icon')
            app_info['md5'] = item.get('md5')
            app_info['name'] = item.get('name')
            app_info['package_name'] = item.get('package')
            app_info['target_sdk'] = item.get('targetSDK')
            app_info['version_code'] = item.get('versionCode')
            app_info['version_name'] = item.get('versionName')
            app_info['file_size'] = item.get('size')

            logger.info(f"Appgallery - Successfully found app with id: {app_id}, "
                        f"package name: {app_info['package_name']},"
                        f" version:{app_info['version_name']},"
                        f" name: {app_info['name']}")
            return app_info

    raise RuntimeError(f'Appgallery - Cannot find application {app_id}')


def appgallery_download_app(app_id, download_path, file_name=None):
    logger.info(f'Appgallery - Try to download application with id {app_id}')
    app_info = get_app_info(app_id)
    r = requests.get(f'https://appgallery.cloud.huawei.com/appdl/{app_id}')
    if r.status_code != 200:
        raise RuntimeError(f'Appgallery - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Appgallery - Creating directory {download_path} for downloading app from Appgallery')

    if file_name is None:
        file_path = f"{download_path}/{app_info['package_name']}-{app_info['version_name']}.apk"
    else:
        file_path = f"{download_path}/{file_name}.apk"

    f = open(f'{file_path}', 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()

    logger.info(f'Appgallery - Apk was downloaded from Appgallery to {file_path}')

    return file_path
