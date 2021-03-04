from base64 import b64encode
import requests
import urllib3
import sys
import os

try:
    from ..helpers.logging import Log
    from .base import DistributionSystem
except ImportError:
    from mdast_cli.helpers.logging import Log
    from mdast_cli.distribution_systems.base import DistributionSystem

urllib3.disable_warnings()


class NexusRepository(DistributionSystem):
    session = None
    nexus_url = None
    download_path = 'downloaded_apps'

    def __init__(self, nexus_url, login, password, repo_name, group_id, artifact_id, version):
        super().__init__(artifact_id, version)

        self.nexus_url = nexus_url if not nexus_url.endswith('/') else nexus_url[:-1]
        self.login = b64encode(str.encode(login))
        self.password = b64encode(str.encode(password))
        self.repo_name = repo_name
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version

        self.connect()

    def connect(self):
        self.session = requests.session()

        api_url = self.nexus_url + '/service/rapture/session'
        body = {
            'username': self.login,
            'password': self.password
        }

        json_response = self.session.post(api_url, data=body, verify=False)
        if json_response.status_code == 403:
            Log.error('NexusRepo: Incorrect authentication credentials')
        elif json_response.status_code == 500:
            Log.error("NexusRepo: Nexus Repo server error 500 during authentication")

    def search_component(self):

        search_url = f"{self.nexus_url}/service/rest/v1/search?repository={self.repo_name}&name={self.artifact_id}&version={self.version}&group={self.group_id}"
        json_response = self.session.get(search_url, verify=False)
        component_search_result = json_response.json().get('items', {})
        if component_search_result:
            Log.info(f'NexusRepo: Search length: {len(component_search_result)}')
            Log.info(f'NexusRepo: Successfully find component: {component_search_result}')
            return component_search_result[-1]
        else:
            Log.info(f'NexusRepo: Unable to find component in repository - {self.repo_name}, name - {self.artifact_id}, version - {self.version}&group_id={self.group_id}')
            return None

    def download_app(self):
        download_url = ''
        file_name = ''
        component_search_result = self.search_component()
        for asset in component_search_result.get('assets', {}):
            if asset.get('contentType', '') in ('application/vnd.android.package-archive', 'application/x-itunes-ipa'):
                download_url = asset.get('downloadUrl')
                file_name = download_url.split('/')[-1] if download_url.split('/')[
                                                                   -1] != '' else f'{self.group_id}-{self.version}.apk'
                break
        if not download_url:
            Log.error(f'NexusRepo: Unuble to find download URL: {len(component_search_result)}')
        response = self.session.get(download_url, allow_redirects=True)
        if response.status_code != 200:
            Log.error('NexusRepo: Failed to download application. Request return status code: {0}'.format(
                response.status_code))
            sys.exit(4)

        path_to_save = os.path.join(self.download_path, file_name)

        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

        return path_to_save
