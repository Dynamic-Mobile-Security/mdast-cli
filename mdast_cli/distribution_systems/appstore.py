import os
import plistlib
import sys
import time
import zipfile

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .appstore_client.store import StoreClient, StoreException

try:
    from ..helpers.logging import Log
    from .base import DistributionSystem
except ImportError:
    from mdast_cli.distribution_systems.base import DistributionSystem
    from mdast_cli.helpers.logging import Log


def get_zipinfo_datetime(timestamp=None):
    timestamp = int(timestamp or time.time())
    return time.gmtime(timestamp)[0:6]


def download_file(url, download_path, file_path):
    with requests.get(url, stream=True) as r:
        if r.status_code != 200:
            Log.error(f'Failed to download application. Request return status code: {r.status_code}"')
            sys.exit(4)
        if not os.path.exists(download_path):
            os.mkdir(download_path)
            Log.info(f'Creating directory {download_path} for downloading app from AppStore')
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                f.write(chunk)
        f.close()
        if os.path.exists(file_path):
            Log.info('Application successfully downloaded')
        else:
            Log.info('Failed to download application. '
                     'Seems like something is wrong with your file path or app file is broken')

    return file_path


def _login_iTunes(Store, apple_id, pass2FA):
    Log.info('Logging into iTunes')
    Store.authenticate(apple_id, pass2FA)
    Log.info(f'Successfully logged in as {Store.account_name}')


class AppStore(DistributionSystem):
    """
    Downloading application(.ipa file) from AppStore
    """

    def __init__(self, appstore_apple_id, appstore_password2FA,
                 appstore_app_id=None, appstore_bundle_id=None, appstore_file_name=None):
        self.apple_id = appstore_apple_id
        self.pass2FA = appstore_password2FA
        self.app_id = appstore_app_id
        self.bundle_id = appstore_bundle_id
        self.appstore_file_name = appstore_file_name
        self.download_path = 'downloaded_apps'

        super().__init__(appstore_app_id, '')
        self.sess = requests.Session()

        retry_strategy = Retry(
            connect=4,
            read=2,
            total=8,
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.sess.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    def download_app(self):
        try:
            Store = StoreClient(self.sess)
            _login_iTunes(Store, self.apple_id, self.pass2FA)
        except StoreException as e:
            Log.error("Store %s failed! Message: %s%s" % (
                e.req, e.err_msg, " (errorType %s)" % e.err_type if e.err_type else ''))
            Log.info('Failed to download application. Seems like your credentials are incorrect '
                     'or your 2FA code expired.')
            sys.exit(4)

        try:
            if self.app_id is None:
                Log.info(f'Trying to find app in App Store with bundle id {self.bundle_id}')
                found_by_bundle_resp = Store.find_app_by_bundle(self.bundle_id)
                resp_info = found_by_bundle_resp.json()
                if found_by_bundle_resp.status_code != 200 or resp_info['resultCount'] != 1:
                    Log.error('Application with your bundle id not found, probably you enter invalid bundle')
                    sys.exit(4)
                app_info = resp_info['results'][0]
                Log.info(f'Successfully found application by bundle id ({self.bundle_id}) '
                         f'with name: "{app_info["trackName"]}", version: {app_info["version"]},'
                         f' app_id: {app_info["trackId"]}')
                self.app_id = app_info["trackId"]

            Log.info(f'Trying to purchase app with id {self.app_id}')
            purchase_resp = Store.purchase(self.app_id)
            if purchase_resp.status_code == 200:
                Log.info(f'App was successfully purchased for {self.apple_id} account')
            elif purchase_resp.status_code == 500:
                Log.info(f'This app was purchased before for {self.apple_id} account')
            Log.info(f'Retrieving download info for app with id: {self.app_id}')
            download_resp = Store.download(self.app_id)
            if not download_resp.songList:
                Log.error('Failed to get app download info! Check your parameters')
                sys.exit(3)
            downloaded_app_info = download_resp.songList[0]

            app_name = downloaded_app_info.metadata.bundleDisplayName
            app_id = downloaded_app_info.songId
            app_bundle_id = downloaded_app_info.metadata.softwareVersionBundleId
            app_version = downloaded_app_info.metadata.bundleShortVersionString

            Log.info(
                f'Downloading app is {app_name} ({app_bundle_id}) with app_id {app_id} and version {app_version}')

            if self.appstore_file_name is None:
                file_name = '%s-%s.ipa' % (app_name, app_version)
            else:
                file_name = '%s-%s.ipa' % (self.appstore_file_name, app_version)

            file_path = os.path.join(self.download_path, file_name)
            Log.info(f'Downloading ipa to {file_path}')
            download_file(downloaded_app_info.URL, self.download_path, file_path)

            with zipfile.ZipFile(file_path, 'a') as ipa_file:
                Log.info('Creating iTunesMetadata.plist with metadata info')
                metadata = downloaded_app_info.metadata.as_dict()
                metadata["apple-id"] = self.apple_id
                metadata["userName"] = self.apple_id
                ipa_file.writestr(zipfile.ZipInfo("iTunesMetadata.plist", get_zipinfo_datetime()),
                                  plistlib.dumps(metadata))

                appContentDir = [c for c in ipa_file.namelist() if
                                 c.startswith('Payload/') and len(c.strip('/').split('/')) == 2][0]
                appContentDir = appContentDir.rstrip('/')

                scManifestData = ipa_file.read(appContentDir + '/SC_Info/Manifest.plist')
                scManifest = plistlib.loads(scManifestData)

                sinfs = {c.id: c.sinf for c in downloaded_app_info.sinfs}
                for i, sinfPath in enumerate(scManifest['SinfPaths']):
                    ipa_file.writestr(appContentDir + '/' + sinfPath, sinfs[i])

        except StoreException as e:
            Log.error("Store %s failed! Message: %s%s" % (
                e.req, e.err_msg, " (errorType %s)" % e.err_type if e.err_type else ''))
            Log.info('Failed to download application. Seems like your app_id does not exist or you did not purchase '
                     'this app from apple account before.')
            sys.exit(4)

        return file_path
