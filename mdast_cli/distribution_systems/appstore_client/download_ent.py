"""Verified iOS ent/download path, adapted from pinned ipatool v2.7.0."""
import base64
import plistlib
from urllib.parse import urlsplit

from requests.adapters import HTTPAdapter

from .download_fallback import _endpoint, _error, _lookup_version, _plist, _validate_result, _version_id, TIMEOUT
from .sap import SAPError, generate_kbsync
from .store import APPSTORE_USER_AGENT

ENT_PATH = '/WebObjects/DownloadDispatch.woa/wa/ent/download'


def download_ent(client, endpoint, app_id, requested_version=''):
    endpoint = _endpoint(endpoint, ENT_PATH)
    app_id = _version_id(app_id)
    latest, bundle_id = _lookup_version(client, app_id)
    version = _version_id(requested_version) if requested_version else latest
    if not client.sess.headers.get('X-Token'):
        raise _error('ent/download', 'Apple session has no download token')
    try:
        blob = generate_kbsync(client.guid, client.dsid)
        hardware = bytes.fromhex(client.guid)
    except SAPError as exc:
        raise _error('ent/download', str(exc)) from None
    serial = base64.b64encode(bytes.fromhex('54c8b0a988') + hardware[2:]).decode('ascii')
    client.sess.mount(endpoint, HTTPAdapter(max_retries=0))
    response = client.sess.post(endpoint, params={'guid': client.guid}, headers={
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'User-Agent': APPSTORE_USER_AGENT,
        'X-Dsid': str(client.dsid), 'iCloud-DSID': str(client.dsid),
        'X-Apple-Store-Front': client.store_front,
    }, data=plistlib.dumps({
        'creditDisplay': '', 'guid': client.guid, 'kbsync': blob,
        'salableAdamId': app_id, 'serialNumber': serial, 'externalVersionId': version,
    }), timeout=TIMEOUT, verify=True, allow_redirects=False)
    data = _plist(response, 'ent/download')
    if data.get('status') not in (None, 0):
        raise _error('ent/download', 'Apple rejected the download status')
    data = _validate_result(response, data, app_id, version, bundle_id, 'ent/download')
    # A signed asset URL may contain sensitive query parameters. Validate its
    # origin without exposing it, and never send account headers to the CDN.
    try:
        url = urlsplit(data['songList'][0]['URL'])
        host = (url.hostname or '').lower()
        if (url.scheme != 'https' or url.username or url.password or url.fragment
                or url.port not in (None, 443)
                or not (host.endswith('.apple.com') or host.endswith('.mzstatic.com'))):
            raise ValueError
    except (ValueError, TypeError):
        raise _error('ent/download', 'Apple returned an invalid asset URL') from None
    return data
