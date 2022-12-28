import logging
import os

import requests

logger = logging.getLogger(__name__)


def appgallery_download_app(app_id, download_path, file_name=None):
    logger.info(f'Appgallery - Start downloading application with id {app_id}')
    r = requests.get(f'https://appgallery.cloud.huawei.com/appdl/{app_id}')
    if r.status_code != 200:
        raise RuntimeError(f'Appgallery - Failed to download application. '
                           f'Something goes wrong. Request return status code: {r.status_code}')

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Appgallery - Creating directory {download_path} for downloading app from Appgallery')

    if file_name is None:
        file_path = f"{download_path}/{app_id}.apk"
    else:
        file_path = f"{download_path}/{file_name}_{app_id}.apk"

    f = open(f'{file_path}', 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()

    logger.info(f'Appgallery - Apk was downloaded from Appgallery to {file_path}')

    return file_path
