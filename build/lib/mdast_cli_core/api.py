import requests
import json
from .base import mDastBase

class mDastAPI(mDastBase):
    """
    Class for interact with mDast system through REST API
    """

    def __init__(self, base_url, username, password):
        super().__init__(base_url)
        self.headers = {}
        self.username = username
        self.password = password
        self.current_context = {}

        self._auth()
        self._current_context()

    def _auth(self):
        """
        Get method for Stingray REST API.
        Made 3 attempts before fail the script
        :return: response
        """
        self.headers['Content-Type'] = 'application/json'
        payload = {'username': self.username, 'password': self.password}

        resp = requests.post(f'{self.url}/login/', headers=self.headers, data=json.dumps(payload, indent=4))
        resp_body = resp.json()

        self.headers['Authorization'] = 'Bearer {0}'.format(resp_body['access'])

    def login(self, username, password):
        self.headers = {'Content-Type': 'application/json'}
        new_payload = {'username': username, 'password': password}
        self.username = username
        self.password = password
        resp = requests.post(f'{self.url}/login/', headers=self.headers, data=json.dumps(new_payload, indent=4))
        if resp.status_code == 200:
            self.set_headers(resp.json()['access'])
            current_context_resp = requests.get(f'{self.url}/currentuser/', headers=self.headers)
            self.current_context = current_context_resp.json()
        return resp

    def _current_context(self):
        current_context_resp = requests.get(f'{self.url}/currentuser/', headers=self.headers)
        self.current_context = current_context_resp.json()

    def set_headers(self, access_token):
        self.headers['Authorization'] = 'Bearer {0}'.format(access_token)
