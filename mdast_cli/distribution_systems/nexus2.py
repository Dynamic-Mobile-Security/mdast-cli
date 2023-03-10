import logging
import os
from base64 import b64encode

import requests
import urllib3

urllib3.disable_warnings()

logger = logging.getLogger(__name__)


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


class Nexus2Repository(object):
    nexus_url = None

    def __init__(self, nexus_url, login, password):
        self.nexus_url = nexus_url if not nexus_url.endswith('/') else nexus_url[:-1]
        self.login = str(login)
        self.password = str(password)

    def download_app(self, download_path, repo_name, group_id, artifact_id, version, extension, file_name=''):
        download_url = f'{self.nexus_url}/service/local/artifact/maven/content?r={repo_name}&g={group_id}&a=' \
                       f'{artifact_id}&v={version}&p={extension}'
        if file_name == '':
            file_name = f'{artifact_id}-{version}.{extension}'
        headers = {
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Authorization': basic_auth(self.login, self.password),
            'Connection': 'close'
        }
        response = requests.get(download_url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f'NexusRepo: Failed to download application. '
                               f'Request return status code: {response.status_code}')
        logger.info(f'Nexus 2 - Downloading app from repo - {repo_name}, with group - {group_id},'
                    f' artifact - {artifact_id}, version - {version} and extension - {extension}')
        path_to_save = os.path.join(download_path, file_name)

        if not os.path.exists(download_path):
            logger.info(f'Nexus 2 - Creating directory {download_path} for downloading app from Nexus 2')
            os.mkdir(download_path)

        with open(path_to_save, 'wb') as f:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)
            f.close()

        logger.info('Nexus 2 - Application was successfully downloaded!')

        return path_to_save
