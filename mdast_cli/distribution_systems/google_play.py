import logging
import os
import shutil
from datetime import datetime

from mdast_cli.distribution_systems.gpapi.googleplay import GooglePlayAPI

logger = logging.getLogger(__name__)


class GooglePlay(object):
    def __init__(self, email=None, password=None, gsfId=None, authSubToken=None):
        self.gp_api = GooglePlayAPI()
        self.email = email
        self.password = password
        self.gsfId = gsfId
        self.authSubToken = authSubToken

    def login(self):
        logger.info('Google Play - Google Play integration, trying to login')
        self.gp_api.login(self.email, self.password, self.gsfId, self.authSubToken)

    def get_gsf_id(self):
        return self.gp_api.gsfId

    def get_auth_subtoken(self):
        return self.gp_api.authSubToken

    def get_app_info(self, package_name):
        self.login()
        app_data = self.gp_api.details(package_name)
        app_details = app_data.get('details', {}).get('appDetails', {})
        image = app_data.get('image', [{}])[0]
        return {
            'integration_type': 'google_play',
            'package_name': app_details.get('packageName', package_name),
            'version_name': app_details.get('versionString'),
            'version_code': app_details.get('versionCode'),
            'file_size': app_details.get('installationSize'),
            'icon_url': image.get('imageUrl')
        }

    def download_app(self, download_path, package_name, google_play_vc_null=None, file_name=None, proxy=None):
        file_name = file_name or package_name
        if google_play_vc_null:
            google_play_vc_null = ''
        downloaded_file, app_details = self.gp_api.download(package_name, google_play_vc_null, proxy=proxy)
        app_version = app_details.get('versionString')
        app_release_ts = self._get_upload_timestamp(app_details)

        if not downloaded_file['splits']:
            path_to_file = f'{download_path}/{file_name}-v{app_version}.apk'
            logger.info('Google Play - Successfully logged in Play Store')
            logger.info(f'Google Play - Downloading {package_name} apk to {path_to_file}')

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
            download_apks_dir = f'{download_path}/{file_name}-v{app_version}'
            logger.info('Google Play - Successfully logged in Play Store')
            logger.info(f'Google Play - Downloading {package_name} app with split apks to {download_apks_dir}')

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

            os.utime(f'{download_apks_dir}/base-master.apk', (app_release_ts, app_release_ts))

            for split in downloaded_file['splits']:
                split_apk_name = split['name']
                with open(f'{download_apks_dir}/{split_apk_name}.apk', 'wb') as file:
                    for chunk in split.get('file').get('data'):
                        file.write(chunk)

                os.utime(f'{download_apks_dir}/{split_apk_name}.apk', (app_release_ts, app_release_ts))

            logger.info('Google Play - Application with split successfully downloaded!')

            shutil.make_archive(download_apks_dir, 'zip', download_apks_dir)
            logger.info(f'Google Play - Archive {download_apks_dir}.zip was successfully created!')
            path_to_file = f'{download_apks_dir}.zip'
            os.utime(path_to_file, (app_release_ts, app_release_ts))
            shutil.rmtree(download_apks_dir)
            logger.info(f'Google Play - Directory {download_apks_dir} was deleted')

        return path_to_file

    @staticmethod
    def _get_upload_timestamp(info):
        try:
            upload_date = info.get('uploadDate')
            dt = datetime.strptime(upload_date, '%b %d, %Y')  # Try to parse upload date
        except Exception:
            # We cannot get upload date, let's use 1st day of current month
            now = datetime.now()
            dt = datetime(year=now.year, month=now.month, day=1)

        return int(dt.timestamp())
