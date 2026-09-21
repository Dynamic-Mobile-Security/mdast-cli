"""Bounded iOS redownload recovery, based on ipatool (see mdast_cli/distribution_systems/appstore_client/IPATOOL-LICENSE)."""
import logging
import plistlib
import re
from urllib.parse import parse_qs

from requests.adapters import HTTPAdapter

from .store import APPSTORE_USER_AGENT, BAG_URL_TEMPLATE, StoreException
from .storefronts import STOREFRONT_COUNTRIES

logger = logging.getLogger(__name__)
LOOKUP_URL = 'https://uclient-api.itunes.apple.com/WebObjects/MZStorePlatform.woa/wa/lookup'
DISPATCH_URL = 'https://downloaddispatch.itunes.apple.com'
TIMEOUT = (10, 60)


def is_empty_download(status, data):
    """Do not turn a license, session, or explicit server refusal into a fallback."""
    return (status == 200 and isinstance(data, dict) and not data.get('songList')
            and not data.get('failureType') and not data.get('customerMessage')
            and not data.get('cancel-purchase-batch') and data.get('m-allowed') is not False
            and data.get('status') in (None, 0))


def _error(phase, message, failure=None):
    return StoreException(phase, message, str(failure) if failure else None)


def _endpoint(value, path):
    # Exact endpoints from Apple's bag only. In particular, never forward auth
    # headers to a URL with a userinfo, query, port, redirect, or different host.
    if value != DISPATCH_URL + path:
        raise _error('download recovery', 'Invalid Apple download endpoint in bag')
    return value


def _plist(response, phase, document=False):
    try:
        content = response.content
        if document and b'<Document' in content:
            match = re.search(rb'<plist\b.*?</plist>', content, re.DOTALL)
            if not match:
                raise ValueError
            content = match.group(0)
        data = plistlib.loads(content)
        if not isinstance(data, dict):
            raise ValueError
        return data
    except (ValueError, TypeError, plistlib.InvalidFileException):
        raise _error(phase, 'Apple returned an invalid plist (HTTP %s)' % response.status_code) from None


def _get(client, url, **kwargs):
    client.sess.mount(url.split('?')[0], HTTPAdapter(max_retries=0))
    response = client.sess.get(url, timeout=TIMEOUT, verify=True, allow_redirects=False, **kwargs)
    if response.status_code != 200:
        raise _error('download recovery', 'Apple metadata request failed (HTTP %s)' % response.status_code)
    return response


def _version_id(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise _error('version lookup', 'Apple returned an invalid external version ID')
    value = str(value)
    if not re.fullmatch(r'[0-9]+', value) or int(value) <= 0:
        raise _error('version lookup', 'Apple returned an invalid external version ID')
    return value


def _lookup_version(client, app_id):
    storefront = str(client.store_front or '').split('-', 1)[0]
    country = STOREFRONT_COUNTRIES.get(storefront)
    if not country:
        raise _error('version lookup', 'Cannot resolve the country of the authenticated Apple storefront')
    for catalog in ('enterprisestore', 'iphone', 'ipad'):
        response = _get(client, LOOKUP_URL, params={
            'version': '2', 'id': str(app_id), 'p': 'mdm-lockup', 'caller': 'MDM',
            'platform': catalog, 'cc': country.lower(), 'l': 'en',
        }, headers={'User-Agent': APPSTORE_USER_AGENT})
        try:
            data = response.json()
            results = data.get('results', {})
            if not isinstance(results, dict):
                raise ValueError
            item = results.get(str(app_id)) or {}
            offers = item.get('offers') or []
            if not offers:
                continue
            offer = offers[0]
            value = (offer.get('version') or {}).get('externalId')
            if value in (None, ''):
                params = offer.get('buyParams') or ''
                if not isinstance(params, str) or re.search(r'%(?![0-9a-fA-F]{2})', params):
                    raise ValueError
                value = parse_qs(params).get('appExtVrsId', [''])[0]
            version = _version_id(value)
            bundle_id = item.get('bundleId')
            if not isinstance(bundle_id, str) or not bundle_id:
                raise ValueError
        except (ValueError, TypeError, AttributeError, IndexError, KeyError):
            raise _error('version lookup', 'Apple returned invalid iOS version metadata') from None
        logger.info('Resolved iOS download version using the %s catalog', catalog)
        return version, bundle_id
    raise _error('version lookup', 'App has no iOS offer in the authenticated Apple storefront')


def _download_request(client, endpoint, app_id, version):
    client.sess.mount(endpoint, HTTPAdapter(max_retries=0))
    return client.sess.post(endpoint, params={'guid': client.guid}, headers={
        'Content-Type': 'application/x-apple-plist', 'User-Agent': APPSTORE_USER_AGENT,
        'X-Dsid': str(client.dsid), 'iCloud-DSID': str(client.dsid),
    }, data=plistlib.dumps({
        'creditDisplay': '', 'guid': client.guid, 'salableAdamId': int(app_id),
        'serialNumber': '0', 'appExtVrsId': version,
    }), timeout=TIMEOUT, verify=True, allow_redirects=False)


def _unavailable(status, data):
    message = str(data.get('customerMessage') or '').strip().lower()
    return (status == 200 and not data.get('failureType') and not data.get('songList')
            and not data.get('cancel-purchase-batch')
            and (message == 'no longer available' or message.endswith(' no longer available')))


def _validate_result(response, data, app_id, version, bundle_id, phase):
    failure = data.get('failureType')
    if failure or data.get('cancel-purchase-batch') or data.get('m-allowed') is False:
        raise _error(phase, data.get('customerMessage') or 'Apple rejected the download', failure)
    if response.status_code != 200 or data.get('customerMessage'):
        raise _error(phase, data.get('customerMessage') or 'Apple download request failed (HTTP %s)' % response.status_code)
    items = data.get('songList')
    if not isinstance(items, list) or len(items) != 1 or not isinstance(items[0], dict):
        raise _error(phase, 'Apple download response must contain exactly one item')
    item = items[0]
    metadata = item.get('metadata') or {}
    if (not isinstance(metadata, dict) or str(metadata.get('itemId')) != str(app_id)
            or str(metadata.get('softwareVersionExternalIdentifier')) != version
            or metadata.get('softwareVersionBundleId') != bundle_id
            or (item.get('songId') is not None and str(item['songId']) != str(app_id))):
        raise _error(phase, 'Apple download response does not match the requested app, version, or bundle')
    if not isinstance(item.get('URL'), str) or not item['URL']:
        raise _error(phase, 'Apple download response has no file URL')
    return data


def recover_empty_download(client, app_id, requested_version=''):
    """Return a verified plist or None if Apple advertises no redownload route."""
    bag_response = _get(client, BAG_URL_TEMPLATE % client.guid,
                        headers={'Accept': 'application/xml', 'User-Agent': APPSTORE_USER_AGENT})
    bag = _plist(bag_response, 'download bag', document=True)
    values = bag.get('urlBag') or bag.get('URLBag') or bag
    if not isinstance(values, dict):
        raise _error('download bag', 'Apple bag has no download configuration')
    if not values.get('redownloadProduct'):
        return None
    redownload = _endpoint(values['redownloadProduct'], '/r/redownload')
    latest, bundle_id = _lookup_version(client, app_id)
    version = _version_id(requested_version) if requested_version else latest
    logger.info('Apple returned no download items; trying the pinned iOS redownload route')
    response = _download_request(client, redownload, app_id, version)
    phase = 'redownloadProduct'
    empty_error = response.status_code == 500 and not response.content
    data = {} if empty_error else _plist(response, phase)
    if values.get('updateProduct') and (empty_error or _unavailable(response.status_code, data)):
        update = _endpoint(values['updateProduct'], '/up/updateProduct')
        logger.info('Apple redownload unavailable; trying the pinned iOS update route')
        response = _download_request(client, update, app_id, version)
        phase = 'updateProduct'
        data = _plist(response, phase)
    return _validate_result(response, data, app_id, version, bundle_id, phase)
