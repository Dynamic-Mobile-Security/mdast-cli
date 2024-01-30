import logging
import os
import pickle
import plistlib
import shutil
import zipfile
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from mdast_cli.distribution_systems.appstore_client.store import StoreClient, StoreException

logger = logging.getLogger(__name__)


def download_file(url, download_path, file_path):
    with requests.get(url, stream=True, verify=False) as r:
        if r.status_code != 200:
            raise RuntimeError(f'Failed to download application. Request return status code: {r.status_code}"')
        if not os.path.exists(download_path):
            os.mkdir(download_path)
            logger.info(f'Creating directory {download_path} for downloading app from AppStore')
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                f.write(chunk)
        f.close()
        if os.path.exists(file_path):
            logger.info('Application successfully downloaded')
        else:
            logger.info('Failed to download application. '
                        'Seems like something is wrong with your file path or app file is broken')

    return file_path


class AppStore(object):
    """
    Downloading application(.ipa file) from AppStore
    """

    def __init__(self, appstore_apple_id, appstore_password2FA):
        self.apple_id = appstore_apple_id
        self.pass2FA = appstore_password2FA
        sess = requests.Session()
        self.store = StoreClient(sess)
        self.login_by_session = False

        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    @lru_cache
    def login(self, force=False):
        self.login_by_session = False
        session_cache = os.path.join('appstore_sessions/', self.apple_id.split("@")[0].replace(".", ""))
        if force and os.path.exists(session_cache):
            shutil.rmtree(session_cache)

        if session_cache and os.path.exists(f'{session_cache}/session.pkl'):
            logger.info(f'Trying to load session for {self.apple_id} iTunes account')
            with open(f'{session_cache}/session.pkl', "rb") as file:
                try:
                    self.store = pickle.load(file)
                    self.login_by_session = True
                    logger.info(f'Loaded session for {self.apple_id}')
                except Exception:
                    shutil.rmtree(session_cache)
                    logger.info('Session was corrupted, deleting it')

        if self.login_by_session:
            return

        try:
            logger.info('Logging into iTunes')
            self.store.authenticate(self.apple_id, self.pass2FA)
            logger.info(f'Successfully logged in as {self.store.account_name}')

            os.makedirs(session_cache, exist_ok=True)
            with open(f'{session_cache}/session.pkl', "wb") as file:
                pickle.dump(self.store, file)
                logger.info(f'Dumped session for {self.apple_id}')
        except StoreException as e:
            raise RuntimeError(f'Failed to download application. Seems like your credentials are incorrect '
                               f'or your 2FA code expired. Message: {e.req} {e.err_msg} {e.err_type}')

    def get_app_info(self, app_id=None, bundle_id=None, country='US'):
        if not app_id and not bundle_id:
            raise 'One of properties ApplicationID or BundleID should be set'

        self.login(True)
        resp_info = self.store.find_app(app_id=app_id, bundle_id=bundle_id, country=country).json()
        try:
            app_info = resp_info['results'][0]
        except IndexError:
            raise RuntimeError('App Store - Application not found') from None
        return {
            'integration_type': 'app_store',
            'appstore_id': app_info['trackId'],
            'package_name': app_info['bundleId'],
            'version_name': app_info['version'],
            'min_sdk_version': app_info['minimumOsVersion'],
            'file_size': app_info['fileSizeBytes'],
            'icon_url': app_info['artworkUrl100']
        }

    def _download_app_int(self, download_path, app_id=None, bundle_id=None, country='US', file_name=None):
        if not app_id:
            logger.info(f'Trying to find app in App Store with bundle id {bundle_id}')
            found_by_bundle_resp = self.store.find_app(bundle_id=bundle_id, country=country)
            resp_info = found_by_bundle_resp.json()
            if found_by_bundle_resp.status_code != 200 or resp_info['resultCount'] != 1:
                raise RuntimeError('Application with your bundle id not found, probably you enter invalid bundle')

            app_info = resp_info['results'][0]
            logger.info(f'Successfully found application by bundle id ({bundle_id}) '
                        f'with name: "{app_info["trackName"]}", version: {app_info["version"]},'
                        f' app_id: {app_info["trackId"]}')
            app_id = app_info["trackId"]

        logger.info(f'Trying to purchase app with id {app_id}')
        purchase_resp = self.store.purchase(app_id)
        if purchase_resp.status_code == 200:
            logger.info(f'App was successfully purchased for {self.apple_id} account')
        elif purchase_resp.status_code == 500:
            logger.info(f'This app was purchased before for {self.apple_id} account')
        logger.info(f'Retrieving download info for app with id: {app_id}')
        download_resp = self.store.download(app_id)
        if not download_resp.songList:
            raise RuntimeError('Failed to get app download info! Check your parameters')

        downloaded_app_info = download_resp.songList[0]

        app_name = downloaded_app_info.metadata.bundleDisplayName
        app_id = downloaded_app_info.songId
        app_bundle_id = downloaded_app_info.metadata.softwareVersionBundleId
        app_version = downloaded_app_info.metadata.bundleShortVersionString
        md5 = downloaded_app_info.md5

        logger.info(
            f'Downloading app is {app_name} ({app_bundle_id}) with app_id {app_id} and version {app_version}')

        if not file_name:
            file_name = '%s-%s.ipa' % (app_name, app_version)
        else:
            file_name = '%s-%s.ipa' % (file_name, app_version)

        file_path = os.path.join(download_path, file_name)
        logger.info(f'Downloading ipa to {file_path}')
        download_file(downloaded_app_info.URL, download_path, file_path)

        with zipfile.ZipFile(file_path, 'a') as ipa_file:
            logger.info('Creating iTunesMetadata.plist with metadata info')
            metadata = downloaded_app_info.metadata.as_dict()
            metadata["apple-id"] = self.apple_id
            metadata["userName"] = self.apple_id
            ipa_file.writestr("iTunesMetadata.plist", plistlib.dumps(metadata))

            appContentDir = [c for c in ipa_file.namelist() if
                             c.startswith('Payload/') and len(c.strip('/').split('/')) == 2][0]
            appContentDir = appContentDir.rstrip('/')

            scManifestData = ipa_file.read(appContentDir + '/SC_Info/Manifest.plist')
            scManifest = plistlib.loads(scManifestData)

            sinfs = {c.id: c.sinf for c in downloaded_app_info.sinfs}
            for i, sinfPath in enumerate(scManifest['SinfPaths']):
                ipa_file.writestr(appContentDir + '/' + sinfPath, sinfs[i])

        return file_path, md5

    def download_app(self, download_path, app_id=None, bundle_id=None, country='US', file_name=None):
        file_path, md5 = None, None
        for force in (False, True):  # try first time with possible stored session, second time with forced login
            try:
                self.login(force=force)
                file_path, md5 = self._download_app_int(download_path, app_id, bundle_id, country, file_name)
                break
            except StoreException as e:
                if not self.login_by_session:  # login by credentials, still with error
                    raise RuntimeError(f'Failed to download application. Seems like your app_id does not exist '
                                       f'or you did not purchase this paid app from apple account before. '
                                       f'Message: {e.req} {e.err_msg} {e.err_type}')

        return file_path, md5
