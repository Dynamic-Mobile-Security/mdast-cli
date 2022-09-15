import logging
import os
import shutil

from .base import DistributionSystem
from .gpapi.googleplay import GooglePlayAPI

logger = logging.getLogger(__name__)


class GooglePlay(DistributionSystem):
    def __init__(self, app_identifier='', file_name=None):
        super().__init__(app_identifier, None)
        self.file_name = file_name or app_identifier
        self.gp_api = GooglePlayAPI()

    def login(self, email=None, password=None, gsfId=None, authSubToken=None):
        logger.info('Google Play - Google Play integration, trying to login')
        self.gp_api.login(email, password, gsfId, authSubToken)

    def get_gsf_id(self):
        return self.gp_api.gsfId

    def get_auth_subtoken(self):
        return self.gp_api.authSubToken

    def get_app_info(self, email=None, password=None, gsfId=None, authSubToken=None):
        self.gp_api.login(email, password, gsfId, authSubToken)
        app_data = self.gp_api.details(self.app_identifier)
        return {
            'package_name': app_data['details']['appDetails']['packageName'],
            'version': app_data['details']['appDetails']['versionString'],
            'version_code': app_data['details']['appDetails']['versionCode'],
            'integration_type': 'google_play'
        }

    def check_login(self, email=None, password=None):
        try:
            self.gp_api.login(email, password, None, None)
        except RuntimeError:
            return False
        except TypeError:
            return False

        return True

    def download_app(self, download_path):

        downloaded_file, app_details = self.gp_api.download(self.app_identifier)
        app_version = app_details.get('versionString')

        if not downloaded_file['splits']:
            path_to_file = f'{download_path}/{self.file_name}-v{app_version}.apk'
            logger.info('Google Play - Successfully logged in Play Store')
            logger.info(f'Google Play - Downloading {self.app_identifier} apk to {path_to_file}')

            if not os.path.exists(download_path):
                os.mkdir(download_path)
                logger.info(f'Google Play - Creating directory {download_path} for downloading app from '
                            f'Google Play Store')

            with open(path_to_file, 'wb') as file:
                for chunk in downloaded_file.get('file').get('data'):
                    file.write(chunk)

            if os.path.exists(path_to_file):
                logger.info('Google Play - Application successfully downloaded!')
            else:
                raise RuntimeError('Google Play - Failed to download application. '
                                   'Seems like something is wrong with your file path or app file is broken')
        else:
            download_apks_dir = f'{download_path}/{self.app_identifier}-v{app_version}'
            logger.info('Google Play - Successfully logged in Play Store')
            logger.info(f'Google Play - Downloading {self.app_identifier} app with split apks to {download_apks_dir}')

            if not os.path.exists(download_path):
                os.mkdir(download_path)
                logger.info(
                    f'Google Play - Creating directory {download_path} for downloading app from Google Play Store')

            if not os.path.exists(download_apks_dir):
                os.mkdir(download_apks_dir)
                logger.info(f'Google Play - Creating directory {download_apks_dir} for downloading app with split apks')

            with open(f'{download_apks_dir}/base-master.apk', 'wb') as file:
                for chunk in downloaded_file.get('file').get('data'):
                    file.write(chunk)

            for split in downloaded_file['splits']:
                split_apk_name = split['name']
                with open(f'{download_apks_dir}/{split_apk_name}.apk', 'wb') as file:
                    for chunk in split.get('file').get('data'):
                        file.write(chunk)

            logger.info('Google Play - Application with split successfully downloaded!')

            shutil.make_archive(download_apks_dir, 'zip', download_apks_dir)
            logger.info(f'Google Play - Archive {download_apks_dir}.zip was successfully created!')
            path_to_file = f'{download_apks_dir}.zip'
            shutil.rmtree(download_apks_dir)
            logger.info(f'Google Play -  Directory {download_apks_dir} was deleted')

        return path_to_file
