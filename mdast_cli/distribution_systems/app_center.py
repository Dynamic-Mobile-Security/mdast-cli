import requests
import sys
import os

try:
    from ..helpers.logging import Log
    from .base import DistributionSystem
except ImportError:
    from mdast_cli.helpers.logging import Log
    from mdast_cli.distribution_systems.base import DistributionSystem


class AppCenter(DistributionSystem):
    """
    Downloading application from HockeyApp distribution system
    """
    url = 'https://api.appcenter.ms/v0.1'
    download_path = 'downloaded_apps'

    def __init__(self, token, app_name, owner_name, version, id):
        super().__init__(app_name, version)

        self.id = id
        self.owner_name = owner_name
        self.auth_header = {'X-API-Token': token}

    def get_version_info_by_id(self):
        Log.info('AppCenter - Get information about application')
        url = '{0}/apps/{1}/{2}/releases/{3}'.format(self.url, self.owner_name, self.app_identifier, self.id)
        response = requests.get(url, headers=self.auth_header)
        if response.status_code != 200:
            Log.error(
                'AppCenter - Failed to get information about application release. Request return status code: {0}'.format(
                    response.status_code))
            sys.exit(4)

        version_info = response.json()
        return version_info

    def get_version_info_by_version(self):
        url = '{0}/apps/{1}/{2}/releases?scope=tester'.format(self.url, self.owner_name, self.app_identifier)

        response = requests.get(url, headers=self.auth_header)
        if response.status_code != 200:
            Log.error(
                'AppCenter - Failed to get information about application releases. Request return status code: {0}'.format(
                    response.status_code))
            sys.exit(4)

        versions_info = response.json()
        for version in versions_info:
            if version['version'] != self.app_version:
                continue

            self.id = version['id']
            version_info = self.get_version_info_by_id()
            return version_info

        return None

    def download_app(self):
        if self.id:
            version_info = self.get_version_info_by_id()
        else:
            version_info = self.get_version_info_by_version()

        if not version_info:
            Log.error('AppCenter - Failed to get app version information. Verify that you set up arguments correctly and try again')

        Log.info('AppCenter - Start download application')
        download_url = version_info.get('download_url')

        response = requests.get(download_url, headers=self.auth_header, allow_redirects=True)
        if response.status_code != 200:
            Log.error('AppCenter - Failed to download application. Request return status code: {0}'.format(
                response.status_code))
            sys.exit(4)

        file_name = '{0}-{1}.apk'.format(self.app_identifier, version_info['version'])
        path_to_save = os.path.join(self.download_path, file_name)

        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

        Log.info('AppCenter - Download application successfully completed to {0}'.format(path_to_save))

        return path_to_save


