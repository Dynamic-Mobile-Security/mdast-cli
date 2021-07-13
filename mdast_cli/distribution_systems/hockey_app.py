import requests
import sys
import os

try:
    from ..helpers.logging import Log
    from .base import DistributionSystem
except ImportError:
    from mdast_cli.helpers.logging import Log
    from mdast_cli.distribution_systems.base import DistributionSystem


class HockeyApp(DistributionSystem):
    """
    Downloading application from HockeyApp distribution system
    """
    url = 'https://rink.hockeyapp.net/api/2'
    download_path = 'downloaded_apps'

    def __init__(self, token, app_bundle, app_identifier, version):
        super().__init__(app_bundle, version)

        self.app_identifier = app_identifier
        self.auth_header = {'X-HockeyAppToken': token}

    def get_apps(self):
        """
        Get list of available applications
        :return: list of all applications (dict)
        """
        Log.info('HockeyApp - Get list of available applications')
        response = requests.get('{0}/{1}'.format(self.url, 'apps'), headers=self.auth_header)
        if response.status_code != 200:
            Log.error('HockeyApp - Error while getting application list, status code: {0}'.format(response.status_code))
            sys.exit(4)

        app_list = response.json()
        return app_list.get('apps', [])

    def get_versions_info(self):
        """
        Get all available versions of current application
        :return: list of versions (dict)
        """
        Log.info('HockeyApp - Get all available versions of current application')
        if not self.app_identifier:
            for application in self.get_apps():
                if application['bundle_identifier'] != self.app_identifier:
                    continue
                self.app_identifier = application['public_identifier']

        versions_info_url = '{0}/{1}/{2}/{3}'.format(self.url, 'apps', self.app_identifier, 'app_versions')
        response = requests.get(versions_info_url, headers=self.auth_header)
        if response.status_code != 200:
            Log.error('HockeyApp - Error while getting application versions info, status code: {0}'.format(response.status_code))
            sys.exit(4)

        return response.json().get('app_versions', [None])

    def get_version(self):
        """
        Return specified version of application
        :return: dict() with metainfo about application version
        """
        Log.info('HockeyApp - Get data about specified version')
        if self.app_version == 'latest':
            application_version = self.get_versions_info()[0]
            return application_version

        for version in self.get_versions_info():
            if version['version'] != self.app_version:
                continue

            application_version = version

            return application_version

    def download_app(self):
        """
        Download application
        :return:
        """
        application_for_download = self.get_version()
        if not application_for_download:
            Log.error('HockeyApp - Error while getting specified application version, exit')
            sys.exit(4)

        download_url = '{0}?format=apk'.format(application_for_download['download_url'].replace('/apps/', '/api/2/apps/'))
        Log.info('HockeyApp - Start download application {0} with version {1}'.format(
            self.app_identifier,
            application_for_download['version']))

        response = requests.get(download_url, headers=self.auth_header, allow_redirects=True)
        if response.status_code != 200:
            Log.error('HockeyApp - Failed to download application. Request return status code: {0}'.format(response.status_code))
            sys.exit(4)

        file_name = '{0}-{1}.apk'.format(self.app_identifier, application_for_download['version'])
        path_to_save = os.path.join(self.download_path, file_name)

        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

        Log.info('HockeyApp - Download application successfully completed to {0}'.format(path_to_save))

        return path_to_save
