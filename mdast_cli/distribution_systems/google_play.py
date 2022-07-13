import os
import sys
import shutil

from .gpapi.googleplay import GooglePlayAPI

try:
    from ..helpers.logging import Log
except ImportError:
    from mdast_cli.helpers.logging import Log


def google_play_download(package_name,
                         email=None,
                         password=None,
                         gsfId=None,
                         authSubToken=None,
                         file_name=None,
                         download_with_creds=False):
    try:
        gp_api = GooglePlayAPI()

        Log.info('Google Play - Google Play integration, trying to login')
        gp_api.login(email, password, gsfId, authSubToken)

        if email is not None and password is not None and download_with_creds is False:
            sys.exit(0)
        else:
            download_path = 'downloaded_apps'

            downloaded_file, app_details = gp_api.download(package_name)
            app_version = app_details.get('versionString')

            if not downloaded_file['splits']:
                if file_name is None:
                    file_name = package_name

                path_to_file = f'{download_path}/{file_name}-v{app_version}.apk'
                Log.info('Google Play - Successfully logged in Play Store')
                Log.info(f'Google Play - Downloading {package_name} apk to {path_to_file}')

                if not os.path.exists(download_path):
                    os.mkdir(download_path)
                    Log.info(f'Google Play - Creating directory {download_path} for downloading app from Google Play Store')

                with open(path_to_file, 'wb') as file:
                    for chunk in downloaded_file.get('file').get('data'):
                        file.write(chunk)

                if os.path.exists(path_to_file):
                    Log.info('Google Play - Application successfully downloaded!')
                else:
                    Log.info('Google Play - Failed to download application. '
                             'Seems like something is wrong with your file path or app file is broken')
                    sys.exit(4)
            else:
                path_to_file = f'{download_path}/{package_name}-v{app_version}'
                Log.info('Google Play - Successfully logged in Play Store')
                Log.info(f'Google Play - Downloading {package_name} app with split to {path_to_file}')

                if not os.path.exists(download_path):
                    os.mkdir(download_path)
                    Log.info(
                        f'Google Play - Creating directory {download_path} for downloading app from Google Play Store')

                if not os.path.exists(path_to_file):
                    os.mkdir(path_to_file)
                    Log.info(
                        f'Google Play - Creating directory {path_to_file} for downloading split app')

                with open(f'{path_to_file}/base-master.apk', 'wb') as file:
                    for chunk in downloaded_file.get('file').get('data'):
                        file.write(chunk)

                for split in downloaded_file['splits']:
                    split_name = split['name']
                    with open(f'{path_to_file}/{split_name}.apk', 'wb') as file:
                        for chunk in split.get('file').get('data'):
                            file.write(chunk)

                if os.path.exists(path_to_file):
                    Log.info('Google Play - Application with split successfully downloaded!')
                    shutil.make_archive(path_to_file, 'zip', path_to_file)
                    Log.info('Google Play - Archive was successfully created!')
                else:
                    Log.info('Google Play - Failed to download application. '
                             'Seems like something is wrong with your file path or app file is broken')
                    sys.exit(4)

        return path_to_file

    except Exception as e:
        Log.error(f'Google Play - Failed to download application. Seems like something goes wrong.'
                  f' {e}')
        Log.info('Google Play - Try to reinitialize your account by logging in with your password and email')
        sys.exit(4)
