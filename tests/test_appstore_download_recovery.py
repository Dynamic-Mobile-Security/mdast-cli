"""App Store recovery uses the account region and never changes the requested app."""
import copy
import plistlib
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import responses

from mdast_cli.distribution_systems.appstore_client.download_fallback import (
    DISPATCH_URL, LOOKUP_URL, TIMEOUT,
)
from mdast_cli.distribution_systems.appstore_client.store import StoreClient, StoreException

APP_ID = '123456789'
VERSION = '987654321'
GUID = '123456789ABC'
BUNDLE = 'com.example.app'
VOLUME = 'https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct?guid=' + GUID
BAG = 'https://init.itunes.apple.com/bag.xml?guid=' + GUID
REDOWNLOAD = DISPATCH_URL + '/r/redownload'
UPDATE = DISPATCH_URL + '/up/updateProduct'
EMPTY = {'status': 0, 'authorized': False, 'songList': []}
ITEM = {'songId': int(APP_ID), 'URL': 'https://aod-ssl.itunes.apple.com/app.ipa', 'md5': 'a' * 32,
        'metadata': {'itemId': int(APP_ID), 'softwareVersionExternalIdentifier': int(VERSION),
                     'softwareVersionBundleId': BUNDLE, 'bundleDisplayName': 'Example',
                     'bundleShortVersionString': '1.0'}}


@pytest.fixture
def client():
    session = requests.Session()
    session.headers['X-Token'] = 'test-token'
    store = StoreClient(session, GUID)
    store.store_front = '143441-1,34'
    store.dsid = '42'
    yield store
    session.close()


def plist(url, data, method=responses.POST, status=200):
    responses.add(method, url, body=plistlib.dumps(data), status=status,
                  content_type='application/x-apple-plist')


def bag(redownload=REDOWNLOAD, update=UPDATE):
    plist(BAG, {'urlBag': {'redownloadProduct': redownload, 'updateProduct': update}}, responses.GET)


def catalog(platform, missing=False, country='us', offer=None, bundle=BUNDLE, status=200):
    data = {'results': {}} if missing else {'results': {APP_ID: {
        'bundleId': bundle, 'offers': [offer or {'version': {'externalId': int(VERSION)}}],
    }}}
    responses.add(responses.GET, LOOKUP_URL, json=data, status=status, match=[
        responses.matchers.query_param_matcher({
            'version': '2', 'id': APP_ID, 'p': 'mdm-lockup', 'caller': 'MDM',
            'platform': platform, 'cc': country, 'l': 'en',
        }),
    ])


def prepare(catalogs=('enterprisestore',), **kwargs):
    plist(VOLUME, EMPTY)
    bag()
    for index, platform in enumerate(catalogs):
        catalog(platform, missing=index < len(catalogs) - 1, **kwargs)


@responses.activate
def test_successful_volume_response_does_not_enter_recovery(client):
    plist(VOLUME, {'songList': [ITEM]})
    assert client.download(APP_ID).songList[0].songId == int(APP_ID)
    assert len(responses.calls) == 1


@pytest.mark.parametrize('failure', ['9610', '1008', '2034', '2042', '5002'])
@responses.activate
def test_original_license_and_session_errors_are_preserved(client, failure):
    plist(VOLUME, {'failureType': failure, 'customerMessage': 'Original refusal'})
    with pytest.raises(StoreException) as error:
        client.download(APP_ID)
    assert error.value.err_type == failure
    assert len(responses.calls) == 1


@pytest.mark.parametrize('extra', [
    {'customerMessage': 'Account disabled'}, {'cancel-purchase-batch': True},
    {'m-allowed': False}, {'status': -128},
])
@responses.activate
def test_explicit_refusal_does_not_enter_recovery(client, extra):
    plist(VOLUME, dict(EMPTY, **extra))
    with pytest.raises(StoreException):
        client.download(APP_ID)
    assert len(responses.calls) == 1


@pytest.mark.parametrize('catalogs', [
    ('enterprisestore',), ('enterprisestore', 'iphone'), ('enterprisestore', 'iphone', 'ipad'),
])
@responses.activate
def test_recovers_and_pins_first_available_ios_catalog(client, catalogs):
    prepare(catalogs)
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [ITEM]})
    assert client.download(APP_ID).songList[0].metadata.softwareVersionBundleId == BUNDLE
    request = responses.calls[-1].request
    assert plistlib.loads(request.body)['appExtVrsId'] == VERSION
    assert request.headers['iCloud-DSID'] == '42'
    assert client.sess.get_adapter(REDOWNLOAD).max_retries.total == 0


@responses.activate
def test_retains_the_authenticated_account_region(client):
    client.store_front = '143469-1,34'
    prepare(('enterprisestore', 'iphone'), country='ru')
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [ITEM]})
    client.download(APP_ID)
    lookups = [c.request for c in responses.calls if c.request.url.startswith(LOOKUP_URL)]
    assert all(parse_qs(urlsplit(r.url).query)['cc'] == ['ru'] for r in lookups)


@responses.activate
def test_reads_external_version_from_buy_params(client):
    prepare(offer={'buyParams': 'appExtVrsId=' + VERSION})
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [ITEM]})
    client.download(APP_ID)
    assert plistlib.loads(responses.calls[-1].request.body)['appExtVrsId'] == VERSION


@responses.activate
def test_preserves_explicitly_requested_version(client):
    prepare()
    item = copy.deepcopy(ITEM)
    item['metadata']['softwareVersionExternalIdentifier'] = 123
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [item]})
    client.download(APP_ID, '123')
    assert plistlib.loads(responses.calls[-1].request.body)['appExtVrsId'] == '123'


@pytest.mark.parametrize('unavailable', [None, 'No Longer Available', 'This app is no longer available'])
@responses.activate
def test_update_recovers_only_the_known_redownload_failures(client, unavailable):
    prepare(('enterprisestore', 'iphone'))
    if unavailable is None:
        responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, body=b'', status=500)
    else:
        plist(REDOWNLOAD + '?guid=' + GUID, {'customerMessage': unavailable})
    plist(UPDATE + '?guid=' + GUID, {'songList': [ITEM]})
    assert client.download(APP_ID).songList[0].songId == int(APP_ID)
    assert len(responses.calls) == 6
    assert plistlib.loads(responses.calls[-1].request.body)['appExtVrsId'] == VERSION


@pytest.mark.parametrize('failure', ['9610', '2034'])
@responses.activate
def test_recovery_refusal_preserves_error_and_does_not_try_update(client, failure):
    prepare()
    plist(REDOWNLOAD + '?guid=' + GUID, {'failureType': failure, 'customerMessage': 'Refused'})
    with pytest.raises(StoreException) as error:
        client.download(APP_ID)
    assert error.value.err_type == failure
    assert len(responses.calls) == 4


@pytest.mark.parametrize('url', [
    'http://downloaddispatch.itunes.apple.com/r/redownload',
    'https://evil.example/r/redownload',
    REDOWNLOAD + '?extra=1', REDOWNLOAD + '#fragment',
    'https://user:secret@downloaddispatch.itunes.apple.com/r/redownload',
    'https://downloaddispatch.itunes.apple.com:8443/r/redownload',
    'https://downloaddispatch.itunes.apple.com/up/updateProduct',
])
@responses.activate
def test_invalid_bag_endpoint_is_rejected_before_sending_auth_headers(client, url):
    plist(VOLUME, EMPTY)
    bag(redownload=url)
    with pytest.raises(StoreException, match='Invalid Apple download endpoint'):
        client.download(APP_ID)
    assert len(responses.calls) == 2


@responses.activate
def test_dispatch_redirect_is_not_followed(client):
    prepare()
    responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, status=302,
                  headers={'Location': 'https://evil.example/collect'})
    with pytest.raises(StoreException):
        client.download(APP_ID)
    assert len(responses.calls) == 4


@pytest.mark.parametrize('key,value', [
    ('itemId', 999), ('softwareVersionExternalIdentifier', 999),
    ('softwareVersionBundleId', 'com.example.other'),
])
@responses.activate
def test_rejects_mismatched_app_version_or_bundle(client, key, value):
    prepare()
    item = copy.deepcopy(ITEM)
    item['metadata'][key] = value
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [item]})
    with pytest.raises(StoreException, match='does not match'):
        client.download(APP_ID)


@responses.activate
def test_missing_app_does_not_send_an_unpinned_request(client):
    plist(VOLUME, EMPTY)
    bag()
    for platform in ('enterprisestore', 'iphone', 'ipad'):
        catalog(platform, missing=True)
    with pytest.raises(StoreException, match='no iOS offer'):
        client.download(APP_ID)
    assert len(responses.calls) == 5


@responses.activate
def test_metadata_http_error_is_not_hidden_by_other_catalogs(client):
    prepare(status=503)
    with pytest.raises(StoreException, match='HTTP 503'):
        client.download(APP_ID)
    assert len(responses.calls) == 3


@responses.activate
def test_empty_update_stops_after_one_attempt(client):
    prepare()
    responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, body=b'', status=500)
    plist(UPDATE + '?guid=' + GUID, EMPTY)
    with pytest.raises(StoreException, match='exactly one item'):
        client.download(APP_ID)
    assert len(responses.calls) == 5


@responses.activate
def test_authorized_false_does_not_discard_a_verified_download_item(client):
    # Live updateProduct replies include this flag even when they provide a
    # valid signed IPA. Explicit failures and the item identity are decisive.
    prepare()
    responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, body=b'', status=500)
    plist(UPDATE + '?guid=' + GUID, {'status': 0, 'authorized': False, 'songList': [ITEM]})
    assert client.download(APP_ID).songList[0].songId == int(APP_ID)


@responses.activate
def test_invalid_update_endpoint_is_rejected(client):
    plist(VOLUME, EMPTY)
    bag(update='https://evil.example/up/updateProduct')
    catalog('enterprisestore')
    responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, body=b'', status=500)
    with pytest.raises(StoreException, match='Invalid Apple download endpoint'):
        client.download(APP_ID)
    assert len(responses.calls) == 4


@responses.activate
def test_unknown_storefront_does_not_guess_another_region(client):
    client.store_front = '999999-1,34'
    plist(VOLUME, EMPTY)
    bag()
    with pytest.raises(StoreException, match='country'):
        client.download(APP_ID)
    assert len(responses.calls) == 2


@responses.activate
def test_bag_without_redownload_preserves_original_empty_response_error(client):
    plist(VOLUME, EMPTY)
    bag(redownload='')
    with pytest.raises(StoreException, match='Apple returned no download info'):
        client.download(APP_ID)
    assert len(responses.calls) == 2


@responses.activate
def test_nonempty_http_500_is_not_treated_as_empty_redownload_error(client):
    prepare()
    responses.add(responses.POST, REDOWNLOAD + '?guid=' + GUID, body=b'<html>failure</html>', status=500)
    with pytest.raises(StoreException, match='invalid plist'):
        client.download(APP_ID)
    assert len(responses.calls) == 4


@pytest.mark.parametrize('offer', [
    {'version': {'externalId': False}}, {'version': {'externalId': -1}},
    {'version': {'externalId': 'bad'}}, {'buyParams': 'appExtVrsId=%zz'},
])
@responses.activate
def test_invalid_version_metadata_is_not_sent_to_dispatch(client, offer):
    prepare(offer=offer)
    with pytest.raises(StoreException, match='invalid'):
        client.download(APP_ID)
    assert len(responses.calls) == 3


@responses.activate
def test_new_requests_have_timeout_and_tls_verification(client, monkeypatch):
    prepare()
    plist(REDOWNLOAD + '?guid=' + GUID, {'songList': [ITEM]})
    original = client.sess.request
    calls = []

    def record(method, url, **kwargs):
        calls.append((url, kwargs))
        return original(method, url, **kwargs)

    monkeypatch.setattr(client.sess, 'request', record)
    client.download(APP_ID)
    for _, kwargs in calls[1:]:
        assert kwargs['timeout'] == TIMEOUT
        assert kwargs['verify'] is True
        assert kwargs['allow_redirects'] is False
