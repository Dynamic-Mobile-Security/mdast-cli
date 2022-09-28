import logging
import os
from hashlib import sha1
from time import time

import requests

logger = logging.getLogger(__name__)


class Firebase(object):
    """
    Downloading application from Firebase
    """
    url = 'https://console.firebase.google.com'

    def __init__(self, api_key, SID, HSID, SSID, APISID, SAPISID):
        self.api_key = api_key
        self.SID = SID
        self.HSID = HSID
        self.SSID = SSID
        self.APISID = APISID
        self.SAPISID = SAPISID

    def calculate_sapisid_hash(self):
        """Calculates SAPISIDHASH based on cookies. Required in authorization to download app from firebase"""
        epoch = int(time())
        sha_str = ' '.join([str(int(epoch)), self.SAPISID, self.url])
        sha = sha1(sha_str.encode())
        return f'SAPISIDHASH {int(epoch)}_{sha.hexdigest()}'

    def get_with_auth(self, url):
        SAPISIDHASH = self.calculate_sapisid_hash()

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

        req = requests.get(url, headers=headers, cookies=cookies)
        return req

    def download_app(self, download_path, project_id, app_id, app_code, file_name=None, file_extension=None):
        url_template = f'https://firebaseappdistribution-pa.clients6.google.com/v1/projects/{project_id}' \
                       f'/apps/{app_id}/releases/{app_code}:getLatestBinary?alt=json&key={self.api_key}'

        req = self.get_with_auth(url_template)
        if req.status_code == 200:
            logger.info('Firebase - Start downloading application')
        elif req.status_code == 401:
            raise RuntimeError(f'Firebase - Failed to download application. '
                               f'Seems like you are not authorized. Request return status code: {req.status_code}')

        elif req.status_code == 403:
            raise RuntimeError(f'Firebase - Failed to download application. Seems like you dont have permissions '
                               f'for downloading. Please contact your administrator. '
                               f'Request return status code: {req.status_code}')

        file_url = req.json().get('fileUrl', '')
        if not file_url:
            raise RuntimeError('It seems like Firebase API was changed or request was malformed. '
                               'Please contact your administrator')

        app_file = requests.get(file_url, allow_redirects=True)

        if file_name is None:
            file_name = app_code

        path_to_file = f'{download_path}/{file_name}.{file_extension}'

        if not os.path.exists(download_path):
            os.mkdir(download_path)
            logger.info(f'Firebase - Creating directory {download_path} for downloading app from Firebase')

        with open(path_to_file, 'wb') as file:
            file.write(app_file.content)

        if os.path.exists(path_to_file):
            logger.info('Firebase - Application successfully downloaded')
        else:
            logger.info('Firebase - Failed to download application. '
                        'Seems like something is wrong with your file path or app file is broken')

        return path_to_file
