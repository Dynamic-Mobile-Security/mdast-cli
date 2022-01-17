import os
import sys
from hashlib import sha1
from time import time

import requests

try:
    from ..helpers.logging import Log
    from .base import DistributionSystem
except ImportError:
    from mdast_cli.distribution_systems.base import DistributionSystem
    from mdast_cli.helpers.logging import Log


class Firebase(DistributionSystem):
    """
    Downloading application from Firebase
    """
    download_path = 'downloaded_apps'
    url = 'https://console.firebase.google.com'

    def __init__(self, project_id, app_id, app_code, api_key, SID, HSID, SSID, APISID, SAPISID,
                 file_extension, file_name=None):
        super().__init__(app_id, app_code)

        self.project_id = project_id
        self.app_id = app_id
        self.app_code = app_code
        self.api_key = api_key
        self.SID = SID
        self.HSID = HSID
        self.SSID = SSID
        self.APISID = APISID
        self.SAPISID = SAPISID
        self.file_extension = file_extension
        self.file_name = file_name

    def calculate_sapisid_hash(self):
        """Calculates SAPISIDHASH based on cookies. Required in authorization to download app from firebase"""
        epoch = int(time())
        sha_str = ' '.join([str(int(epoch)), self.SAPISID, self.url])
        sha = sha1(sha_str.encode())
        return f'SAPISIDHASH {int(epoch)}_{sha.hexdigest()}'

    def download_app(self):
        SAPISIDHASH = self.calculate_sapisid_hash()

        url_template = f'https://firebaseappdistribution-pa.clients6.google.com/v1/projects/{self.project_id}' \
                       f'/apps/{self.app_id}/releases/{self.app_code}:getLatestBinary?alt=json&key={self.api_key}'

        headers = {'Origin': self.url,
                   'X-Goog-Authuser': '0',
                   'Authorization': SAPISIDHASH}

        cookies = {
            'SID': self.SID,
            'HSID': self.HSID,
            'SSID': self.SSID,
            'APISID': self.APISID,
            'SAPISID': self.SAPISID
        }

        req = requests.get(url_template, headers=headers, cookies=cookies)

        if req.status_code == 200:
            Log.info('Firebase - Start downloading application')
        elif req.status_code == 401:
            Log.info('Firebase -  Failed to download application. Seems like you are not authorized.'
                     'Request return status code: {0}'.format(req.status_code))
            sys.exit(4)
        elif req.status_code == 403:
            Log.info('Firebase -  Failed to download application. Seems like you dont have permissions for downloading.'
                     'Please contact your administrator. Request return status code: {0}'.format(req.status_code))
            sys.exit(4)

        file_url = req.json().get('fileUrl', '')
        if not file_url:
            Log.info(
                'It seems like Firebase API was changed or request was malformed. Please contact your administrator')
            sys.exit(4)

        app_file = requests.get(file_url, allow_redirects=True)

        if self.file_name is None:
            self.file_name = self.app_code

        path_to_file = '{0}/{1}.{2}'.format(self.download_path, self.file_name, self.file_extension)

        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)
            Log.info(f'Firebase - Creating directory {self.download_path} for downloading app from Firebase')

        with open(path_to_file, 'wb') as file:
            file.write(app_file.content)

        if os.path.exists(path_to_file):
            Log.info('Firebase - Application successfully downloaded')
        else:
            Log.info('Firebase - Failed to download application. '
                     'Seems like something is wrong with your file path or app file is broken')

        return path_to_file
