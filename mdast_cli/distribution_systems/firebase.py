import logging
import os
import warnings

# Suppress pkg_resources deprecation warning from google-auth
# Must be before importing google.auth to catch the warning
warnings.filterwarnings('ignore', message='.*pkg_resources is deprecated.*', category=UserWarning)

import google.auth
import google.auth.transport.requests
import requests
from google.oauth2 import service_account
from tqdm import tqdm

from mdast_cli.helpers.file_utils import ensure_download_dir, cleanup_file
from mdast_cli.helpers.const import HTTP_REQUEST_TIMEOUT, HTTP_DOWNLOAD_TIMEOUT

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
            headers=headers,
            timeout=HTTP_REQUEST_TIMEOUT)
        if last_release_info_resp.status_code != 200:
            raise RuntimeError(f'Firebase - Failed to get application info. Status: {last_release_info_resp.status_code}, '
                             f'Response: {last_release_info_resp.text[:500]}')
        release = last_release_info_resp.json()['releases'][0]
    except KeyError as e:
        raise RuntimeError(f'Firebase - Failed to get application info: unexpected response structure: {e}')
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
    app_file_resp = requests.get(app_download_link, allow_redirects=True, stream=True, timeout=HTTP_DOWNLOAD_TIMEOUT)
    if app_file_resp.status_code != 200:
        raise RuntimeError(f'Firebase - Failed to download application, status code: {app_file_resp.status_code}')

    if file_name is None:
        file_name = app_info['version_name']

    path_to_file = f'{download_path}/{file_name}.{file_extension}'

    ensure_download_dir(download_path)
    logger.info(f'Firebase - Creating directory {download_path} for downloading app from Firebase')

    # Use streaming for large files to avoid memory issues
    try:
        total_size = int(app_file_resp.headers.get('content-length', 0))
        chunk_size = 8192
        with open(path_to_file, 'wb') as file:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, 
                      desc=f'Firebase - Downloading {file_name}.{file_extension}', 
                      disable=total_size == 0) as pbar:
                for chunk in app_file_resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))
    except Exception as e:
        # Cleanup partial file on error
        cleanup_file(path_to_file)
        raise RuntimeError(f'Firebase - Failed to write downloaded file: {e}')

    if os.path.exists(path_to_file):
        logger.info(f'Firebase - Application successfully downloaded to {path_to_file}')
    else:
        logger.info('Firebase - Failed to download application. '
                    'Seems like something is wrong with your file path or app file is broken')

    return path_to_file
