import logging
import os

import requests

logger = logging.getLogger(__name__)


class AppCenter(object):
    """
    Downloading application from AppCenter distribution system
    """
    url = 'https://api.appcenter.ms/v0.1'

    def __init__(self, token, owner_name):
        self.owner_name = owner_name
        self.auth_header = {'X-API-Token': token}

    def get_version_info(self, app_identifier, app_version=None, app_id=None):
        if not app_version and not app_id:
            raise 'One of properties AppVersion or AppID should be set'

        if app_id:
            return self.get_version_info_by_id(app_identifier, app_id)

        return self.get_version_info_by_version(app_identifier, app_version)

    def get_version_info_by_id(self, app_identifier, app_id):
        logger.info('AppCenter - Get information about application')
        url = f'{self.url}/apps/{self.owner_name}/{app_identifier}/releases/{app_id}'
        response = requests.get(url, headers=self.auth_header)
        if response.status_code != 200:
            raise RuntimeError(
                f'AppCenter - Failed to get information about application release.'
                f' Request return status code: {response.status_code}')

        version_info = response.json()
        return version_info

    def get_version_info_by_version(self, app_identifier, app_version):
        url = f'{self.url}/apps/{self.owner_name}/{app_identifier}/releases?scope=tester'
        response = requests.get(url, headers=self.auth_header)
        if response.status_code != 200:
            raise RuntimeError(
                f'AppCenter - Failed to get information about application releases.'
                f' Request return status code: {response.status_code}')

        versions_info = response.json()
        for version in versions_info:
            if version['version'] != app_version:
                continue

            version_info = self.get_version_info_by_id(app_identifier, version['id'])
            return version_info

        return None

    def download_app(self, download_path, app_identifier, app_version=None, app_id=None):
        version_info = self.get_version_info(app_identifier, app_version, app_id)
        if not version_info:
            logger.error('AppCenter - Failed to get app version information.'
                         ' Verify that you set up arguments correctly and try again')

        logger.info('AppCenter - Start download application')
        download_url = version_info.get('download_url')

        response = requests.get(download_url, headers=self.auth_header, allow_redirects=True)
        if response.status_code != 200:
            raise RuntimeError(f'AppCenter - Failed to download application. '
                               f'Request return status code: {response.status_code}')

        file_name = '{0}-{1}.apk'.format(app_identifier, version_info['version'])
        path_to_save = os.path.join(download_path, file_name)

        if not os.path.exists(download_path):
            os.mkdir(download_path)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

        logger.info(f'AppCenter - Download application successfully completed to {path_to_save}')

        return path_to_save
