"""The new Apple route must return the requested IPA without leaking auth."""
import base64
import copy
import plistlib

import pytest
import requests
import responses

from mdast_cli.distribution_systems.appstore_client import download_ent, sap
from mdast_cli.distribution_systems.appstore_client.store import StoreClient, StoreException
from test_appstore_download_recovery import (
    APP_ID, VERSION, GUID, BUNDLE, VOLUME, BAG, ITEM, EMPTY, REDOWNLOAD,
    plist, catalog,
)

ENT = 'https://downloaddispatch.itunes.apple.com' + download_ent.ENT_PATH


@pytest.fixture
def client(monkeypatch):
    store = StoreClient(requests.Session(), GUID)
    store.store_front = '143441-1,34'
    store.dsid = '42'
    store.sess.headers['X-Token'] = 'private-token'
    monkeypatch.setattr(download_ent, 'generate_kbsync', lambda guid, dsid: 'cHJpdmF0ZQ==')
    yield store
    store.sess.close()


def prepare(endpoint=ENT):
    plist(VOLUME, EMPTY)
    plist(BAG, {'urlBag': {'volumeStoreDownloadProduct': endpoint,
                          'redownloadProduct': REDOWNLOAD}}, responses.GET)
    catalog('enterprisestore')


@responses.activate
def test_ent_download_returns_verified_item_and_skips_old_redownload(client):
    prepare()
    plist(ENT + '?guid=' + GUID, {'authorized': False, 'songList': [ITEM]})
    result = client.download(APP_ID)
    assert result.songList[0].metadata.softwareVersionBundleId == BUNDLE
    request = responses.calls[-1].request
    payload = plistlib.loads(request.body)
    assert payload['salableAdamId'] == APP_ID
    assert payload['externalVersionId'] == VERSION
    assert payload['kbsync'] == 'cHJpdmF0ZQ=='
    assert base64.b64decode(payload['serialNumber']) == bytes.fromhex('54c8b0a988') + bytes.fromhex(GUID)[2:]
    assert request.headers['X-Token'] == 'private-token'
    assert request.headers['X-Dsid'] == '42'
    assert request.headers['X-Apple-Store-Front'] == client.store_front
    assert request.headers['Content-Type'] == 'application/x-www-form-urlencoded; charset=utf-8'
    assert client.sess.get_adapter(ENT).max_retries.total == 0
    assert len(responses.calls) == 4


@responses.activate
def test_ent_download_keeps_requested_version(client):
    prepare()
    item = copy.deepcopy(ITEM)
    item['metadata']['softwareVersionExternalIdentifier'] = 123
    plist(ENT + '?guid=' + GUID, {'songList': [item]})
    client.download(APP_ID, '123')
    assert plistlib.loads(responses.calls[-1].request.body)['externalVersionId'] == '123'


@pytest.mark.parametrize('endpoint', [
    'http://downloaddispatch.itunes.apple.com' + download_ent.ENT_PATH,
    'https://evil.example' + download_ent.ENT_PATH,
    ENT + '/', ENT + '?extra=1', ENT + '#fragment',
    ENT.replace('https://', 'https://user:secret@'),
    ENT.replace('.com/', '.com:8443/'),
])
@responses.activate
def test_invalid_ent_endpoint_never_receives_credentials(client, endpoint):
    prepare(endpoint)
    with pytest.raises(StoreException, match='Invalid Apple download endpoint'):
        client.download(APP_ID)
    assert len(responses.calls) == 2


@pytest.mark.parametrize('status', [302, 403, 429, 500])
@responses.activate
def test_http_errors_are_preserved_without_redirect_or_legacy_retry(client, status):
    prepare()
    responses.post(ENT + '?guid=' + GUID, status=status, body='',
                   headers={'Location': 'https://evil.example/token'})
    with pytest.raises(StoreException, match=f'HTTP {status}'):
        client.download(APP_ID)
    assert len(responses.calls) == 4


@pytest.mark.parametrize('data,message', [
    ({'status': 0, 'songList': []}, 'exactly one item'),
    ({'status': -128, 'songList': [ITEM]}, 'status'),
    ({'failureType': '2042', 'customerMessage': 'Sign in required'}, 'Sign in required'),
    ({'m-allowed': False, 'songList': [ITEM]}, 'rejected'),
])
@responses.activate
def test_ent_refusal_or_empty_response_is_never_success(client, data, message):
    prepare()
    plist(ENT + '?guid=' + GUID, data)
    with pytest.raises(StoreException, match=message):
        client.download(APP_ID)
    assert len(responses.calls) == 4


@pytest.mark.parametrize('field,value', [
    ('itemId', 999), ('softwareVersionExternalIdentifier', 999),
    ('softwareVersionBundleId', 'com.example.other'),
])
@responses.activate
def test_ent_result_identity_must_match(client, field, value):
    prepare()
    item = copy.deepcopy(ITEM)
    item['metadata'][field] = value
    plist(ENT + '?guid=' + GUID, {'songList': [item]})
    with pytest.raises(StoreException, match='does not match'):
        client.download(APP_ID)


@pytest.mark.parametrize('asset', [
    'http://aod-ssl.itunes.apple.com/a.ipa', 'https://evil.example/a.ipa',
    'https://user:secret@aod-ssl.itunes.apple.com/a.ipa',
])
@responses.activate
def test_ent_rejects_unsafe_asset_origin_without_exposing_url(client, asset):
    prepare()
    item = dict(ITEM, URL=asset)
    plist(ENT + '?guid=' + GUID, {'songList': [item]})
    with pytest.raises(StoreException, match='invalid asset URL') as error:
        client.download(APP_ID)
    assert asset not in str(error.value)


@responses.activate
def test_helper_failure_does_not_send_blob_or_try_redownload(client, monkeypatch):
    prepare()
    def fail(*args):raise sap.SAPError('SAP helper timed out during kbsync')
    monkeypatch.setattr(download_ent, 'generate_kbsync', fail)
    with pytest.raises(StoreException, match='timed out'):
        client.download(APP_ID)
    assert len(responses.calls) == 3


@responses.activate
def test_ent_request_requires_tls_timeout_and_no_redirects(client, monkeypatch):
    prepare()
    original = client.sess.post
    def post(url, **kwargs):
        if url == ENT:
            assert kwargs['verify'] is True
            assert kwargs['allow_redirects'] is False
            assert kwargs['timeout'] == (10, 60)
        return original(url, **kwargs)
    monkeypatch.setattr(client.sess, 'post', post)
    plist(ENT + '?guid=' + GUID, {'songList': [ITEM]})
    client.download(APP_ID)
