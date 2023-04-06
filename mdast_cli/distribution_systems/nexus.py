import logging
import os
from base64 import b64encode

import requests
import urllib3

urllib3.disable_warnings()

logger = logging.getLogger(__name__)


class NexusRepository(object):
    nexus_url = None

    def __init__(self, nexus_url, login, password):
        self.nexus_url = nexus_url if not nexus_url.endswith('/') else nexus_url[:-1]
        self.login = b64encode(str.encode(login))
        self.password = b64encode(str.encode(password))
        self.session = None

    def connect(self):
        if self.session:  # we already connected
            return

        self.session = requests.session()

        api_url = self.nexus_url + '/service/rapture/session'
        body = {
            'username': self.login,
            'password': self.password
        }

        json_response = self.session.post(api_url, data=body, verify=False)
        if json_response.status_code == 403:
            logger.error('NexusRepo: Incorrect authentication credentials')
        elif json_response.status_code == 500:
            logger.error("NexusRepo: Nexus Repo server error 500 during authentication")

    def search_component(self, repo_name, group_id, artifact_id, version):
        self.connect()
        search_url = f"{self.nexus_url}/service/rest/v1/search?repository={repo_name}&name={artifact_id}" \
                     f"&version={version}&group={group_id}"
        json_response = self.session.get(search_url, verify=False)
        component_search_result = json_response.json().get('items', {})
        if component_search_result:
            logger.info(f'NexusRepo: Search length: {len(component_search_result)}')
            logger.info(f'NexusRepo: Successfully find component: {component_search_result}')
            return component_search_result[-1]
        else:
            logger.info(f'NexusRepo: Unable to find component in repository - {repo_name}, '
                        f'name - {artifact_id}, version - {version}&group_id={group_id}')
            return None

    def download_app(self, download_path, repo_name, group_id, artifact_id, version):
        self.connect()
        download_url = ''
        file_name = ''
        component_search_result = self.search_component(repo_name, group_id, artifact_id, version)
        for asset in component_search_result.get('assets', {}):
            if asset.get('contentType', '') in ('application/vnd.android.package-archive', 'application/x-itunes-ipa'):
                download_url = asset.get('downloadUrl')
                file_name = download_url.split('/')[-1] if download_url.split('/')[
                                                               -1] != '' else f'{group_id}-{version}.apk'
                break
        if not download_url:
            logger.error(f'NexusRepo: Unable to find download URL: {len(component_search_result)}')
        response = self.session.get(download_url, allow_redirects=True)
        if response.status_code != 200:
            raise RuntimeError(f'NexusRepo: Failed to download application. '
                               f'Request return status code: {response.status_code}')

        path_to_save = os.path.join(download_path, file_name)

        if not os.path.exists(download_path):
            os.mkdir(download_path)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

        return path_to_save
