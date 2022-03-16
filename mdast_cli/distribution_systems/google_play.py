import os
import sys
import traceback

from .gpapi.googleplay import GooglePlayAPI

try:
    from ..helpers.logging import Log
except ImportError:
    from mdast_cli.helpers.logging import Log


def google_play_download(package_name, email, password, file_name=None):
    try:
        gp_api = GooglePlayAPI()

        Log.info('Google Play - Logging in Google Play with mail + password')
        gp_api.login(email, password)

        download_path = 'downloaded_apps'

        if file_name is None:
            file_name = package_name
        path_to_file = f'{download_path}/{file_name}.apk'
        Log.info(f'Google Play - Downloading {package_name} apk to {path_to_file}')

        if not os.path.exists(download_path):
            os.mkdir(download_path)
            Log.info(f'Google Play - Creating directory {self.download_path} for downloading app from Google Play Store')

        downloaded_file = gp_api.download(package_name)
        with open(path_to_file, 'wb') as file:
            for chunk in downloaded_file.get('file').get('data'):
                file.write(chunk)

        if os.path.exists(path_to_file):
            Log.info('Google Play - Application successfully downloaded!')
        else:
            Log.info('Google Play - Failed to download application. '
                     'Seems like something is wrong with your file path or app file is broken')
            sys.exit(4)

        return path_to_file

    except Exception as e:
        Log.error(f'Google Play - Failed to download application. Seems like something goes wrong.'
                  f' {e}')
        sys.exit(4)