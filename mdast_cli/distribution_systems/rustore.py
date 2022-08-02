import os
import sys

import requests

try:
    from ..helpers.logging import Log
except ImportError:
    from mdast_cli.helpers.logging import Log


class Rustore():
    """
    Downloading application from Rustore
    """
    download_path = 'downloaded_apps'

    def __init__(self, package_name):
        self.package_name = package_name

    def get_app_info(self):
        app_info = requests.get(f'https://backapi.rustore.ru/applicationData/overallInfo/{self.package_name}')
        if app_info.status_code == 200:
            body_info = app_info.json()['body']
            Log.info(f"Rustore - Successfully found app with package name: {self.package_name},"
                     f" version:{body_info['versionName']}, company: {body_info['companyName']}")
        apk_uid = body_info['apkUid']
        return {
            'package_name': body_info['packageName'],
            'version': body_info['versionName'],
            'download_url': f'https://static.rustore.ru/{apk_uid}'
        }

    def download_app(self):
        app_info = self.get_app_info()
        Log.info('Rustore - Start downloading application')
        r = requests.get(app_info['download_url'])
        if r.status_code == 401:
            Log.info(f'Rustore - Failed to download application. '
                     f'Something goes wrong. Request return status code: {r.status_code}')
            sys.exit(4)
        file_path = f"{self.download_path}/{app_info['package_name']}-{app_info['version']}.apk"

        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)
            Log.info(f'Rustore - Creating directory {self.download_path} for downloading app from Rustore')

        f = open(file_path, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
                f.write(chunk)
        f.close()
        Log.info(f'Rustore - Apk was downloaded from rustore to {file_path}')
        return file_path
