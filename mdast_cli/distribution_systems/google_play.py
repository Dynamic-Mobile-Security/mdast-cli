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
        file_path = os.path.join(download_path, file_name, '.apk')
        Log.info(f'Google Play - Downloading {package_name} apk to {file_path}')

        downloaded_file = gp_api.download(package_name)
        with open(package_name + '.apk', 'wb') as f:
            for chunk in downloaded_file.get('file').get('data'):
                f.write(chunk)

        Log.info('Google Play - Download apk successful!\n')

        return file_path
    except Exception as e:
        Log.error(f'Google Play - Failed to download application. Seems like something goes wrong.'
                  f' {e.with_traceback()}')
        sys.exit(4)
