import logging
import os

import google.auth
import google.auth.transport.requests
import requests
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def get_app_info(project_number, app_id, account_json_path):
    try:
        credentials = service_account.Credentials.from_service_account_file(account_json_path, scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(google.auth.transport.requests.Request())
        google_id_token = credentials.token
        headers = {'Authorization': f'Bearer {google_id_token}'}
        last_release_info_resp = requests.get(
            f'https://firebaseappdistribution.googleapis.com/v1/projects/{project_number}/apps/'
            f'{app_id}/releases?pageSize=1',
            headers=headers)
        release = last_release_info_resp.json()['releases'][0]
    except Exception:
        raise RuntimeError('Firebase - Failed to get application info.')
    return {
        'integration_type': 'firebase',
        'app_name': release['name'],
        'version': release['buildVersion'],
        'create_time': release['createTime'],
        'download_link': release['binaryDownloadUri']
    }


def check_firebase_login(account_json_path):
    credentials = service_account.Credentials.from_service_account_file(account_json_path, scopes=[
        'https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(google.auth.transport.requests.Request())
    google_id_token = credentials.token
    if 'ya29' in google_id_token:
        return True
    else:
        return False


def firebase_download_app(download_path, project_number, app_id, account_json_path, file_name=None,
                          file_extension='apk'):
    logger.info(f'Firebase - Try to download {file_extension} from latest release in project - '
                f'{project_number} with app id {app_id}')
    try:
        credentials = service_account.Credentials.from_service_account_file(account_json_path, scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])
    except Exception:
        raise RuntimeError('Firebase - service account json file does not exist')
    try:
        credentials.refresh(google.auth.transport.requests.Request())
        google_id_token = credentials.token
    except Exception:
        raise RuntimeError('Firebase - incorrect data or no permissions for your account')
    headers = {'Authorization': f'Bearer {google_id_token}'}
    last_release_info_resp = requests.get(
        f'https://firebaseappdistribution.googleapis.com/v1/projects/{project_number}/apps/'
        f'{app_id}/releases?pageSize=1',
        headers=headers)
    if last_release_info_resp.status_code != 200:
        raise RuntimeError('Firebase - no release found or incorrect project_number/app_id')
    release = last_release_info_resp.json()['releases'][0]
    app_download_link = release['binaryDownloadUri']
    logger.info(f"Firebase - found release {release['name']} with version - {release['displayVersion']}")

    app_file = requests.get(app_download_link, allow_redirects=True)

    if file_name is None:
        file_name = release['displayVersion']

    path_to_file = f'{download_path}/{file_name}.{file_extension}'

    if not os.path.exists(download_path):
        os.mkdir(download_path)
        logger.info(f'Firebase - Creating directory {download_path} for downloading app from Firebase')

    with open(path_to_file, 'wb') as file:
        file.write(app_file.content)

    if os.path.exists(path_to_file):
        logger.info(f'Firebase - Application successfully downloaded to {path_to_file}')
    else:
        logger.info('Firebase - Failed to download application. '
                    'Seems like something is wrong with your file path or app file is broken')

    return path_to_file
