import logging
import os

import google.auth
import google.auth.transport.requests
import requests
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def get_token(account_info):
    if isinstance(account_info, dict):
        credentials = service_account.Credentials.from_service_account_info(account_info, scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])
    else:
        credentials = service_account.Credentials.from_service_account_file(account_info, scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])

    credentials.refresh(google.auth.transport.requests.Request())
    google_id_token = credentials.token
    if 'ya29' in google_id_token:
        return google_id_token

    raise RuntimeError(f'Incorrect token {google_id_token}')


def get_app_info(project_number, app_id, account_info):
    try:
        token = get_token(account_info)
        headers = {'Authorization': f'Bearer {token}'}
        last_release_info_resp = requests.get(
            f'https://firebaseappdistribution.googleapis.com/v1/projects/{project_number}/apps/'
            f'{app_id}/releases?pageSize=1',
            headers=headers)
        release = last_release_info_resp.json()['releases'][0]
    except Exception as e:
        raise RuntimeError(f'Firebase - Failed to get application info: {e}')

    logger.info(f"Firebase - found release {release['name']} with version - {release['displayVersion']}")
    return {
        'integration_type': 'firebase',
        'app_name': release['name'],
        'version_code': release['buildVersion'],
        'version_name': release['displayVersion'],
        'create_time': release['createTime'],
        'download_link': release['binaryDownloadUri']
    }


def firebase_download_app(download_path, project_number, app_id, account_info, file_name=None,
                          file_extension='apk'):
    logger.info(f'Firebase - Try to download {file_extension} from latest release in project - '
                f'{project_number} with app id {app_id}')
    app_info = get_app_info(project_number, app_id, account_info)
    app_download_link = app_info['download_link']
    app_file_resp = requests.get(app_download_link, allow_redirects=True)
    if app_file_resp != 200:
        raise RuntimeError(f'Firebase - Failed to download application, status code - {app_file_resp.status_code} ')

    if file_name is None:
        file_name = app_info['version_name']

    path_to_file = f'{download_path}/{file_name}.{file_extension}'

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Firebase - Creating directory {download_path} for downloading app from Firebase')

    with open(path_to_file, 'wb') as file:
        file.write(app_file_resp.content)

    if os.path.exists(path_to_file):
        logger.info(f'Firebase - Application successfully downloaded to {path_to_file}')
    else:
        logger.info('Firebase - Failed to download application. '
                    'Seems like something is wrong with your file path or app file is broken')

    return path_to_file
