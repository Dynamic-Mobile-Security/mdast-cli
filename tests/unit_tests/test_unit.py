import sys

from pytest_testconfig import config
import math
import requests

from mdast_cli.distribution_systems.google_play import GooglePlayAPI
from mdast_cli.distribution_systems.appstore import AppStore
from mdast_cli.distribution_systems.gpapi.googleplay import encrypt_password
from mdast_cli.distribution_systems.gpapi.config import DeviceBuilder
from mdast_cli.distribution_systems.google_play import google_play_download

from mdast_cli.distribution_systems.appstore_client.store import StoreClient, StoreException
from mdast_cli.distribution_systems.appstore import *

from mdast_cli.helpers.const import *
from mdast_cli.helpers.logging import Log
from mdast_cli.helpers.helpers import get_app_path


# Google Play unit tests
def test_google_play_class_clean_init():
    gp_api = GooglePlayAPI()
    assert gp_api.gsfId is None
    assert gp_api.authSubToken is None
    assert gp_api.device_config_token is None
    assert gp_api.dfeCookie is None
    assert gp_api.deviceCheckinConsistencyToken is None


def test_device_builder_class_clean_init():
    device_builder = GooglePlayAPI().deviceBuilder
    assert device_builder.locale == 'en_US'
    assert device_builder.timezone == 'UTC'


def test_device_builder_fake_device_setup_with_25_API_bacon():
    fake_device_data = GooglePlayAPI(device_codename='bacon').deviceBuilder.device
    assert fake_device_data['userreadablename'] == 'OnePlus One (api25)'
    assert len(fake_device_data) == 36


def test_device_builder_fake_device_setup_with_default_27_API():
    fake_device_data = GooglePlayAPI().deviceBuilder.device
    assert fake_device_data['userreadablename'] == 'Nexus 6P (api27)'
    assert fake_device_data['build.version.sdk_int'] == '27'
    assert fake_device_data['build.version.release'] == '8.1.0'
    assert fake_device_data['gsf.version'] == '12688052'
    assert fake_device_data['timezone'] == 'America/Los_Angeles'
    assert fake_device_data['client'] == 'android-google'
    assert fake_device_data['build.product'] == 'angler'
    assert fake_device_data['build.id'] == 'OPM2.171019.029.B1'
    assert len(fake_device_data) == 36


def test_encrypt_password_without_encoding():
    encrypted_pass = encrypt_password('random_string', 'random_string')
    assert encrypted_pass != ''
    assert type(encrypted_pass) == bytes
    assert len(encrypted_pass) == 180


def test_encrypt_password_with_encoding_and_valid_data():
    encrypted_pass_valid = encrypt_password(config['gp']['test_email'], config['gp']['test_pass']).decode('utf-8')
    assert encrypted_pass_valid != ''
    assert type(encrypted_pass_valid) == str
    assert len(encrypted_pass_valid) == 180


def test_device_builder_init(gp_api):
    device_builder = gp_api.deviceBuilder
    assert device_builder.locale == 'en_US'
    assert device_builder.timezone == 'UTC'
    assert type(device_builder.device) == dict
    assert len(device_builder.device) == 36


def test_device_builder_set_locale(gp_api):
    gp_api.deviceBuilder.setLocale('test_locale')
    assert gp_api.deviceBuilder.locale == 'test_locale'


def test_device_builder_set_invalid_locale(gp_api):
    current_locale = gp_api.deviceBuilder.locale
    try:
        gp_api.deviceBuilder.setLocale('')
    except ValueError as e:
        assert True
        assert e.args[0] == 'locale is not defined'
    assert gp_api.deviceBuilder.locale != ''
    assert gp_api.deviceBuilder.locale == current_locale


def test_device_builder_set_timezone(gp_api):
    gp_api.deviceBuilder.setTimezone('test_timezone')
    assert gp_api.deviceBuilder.timezone == 'test_timezone'


def test_device_builder_get_base_headers(gp_api):
    base_headers = gp_api.deviceBuilder.getBaseHeaders()
    assert base_headers['Accept-Language'] == 'en-US'
    assert base_headers['X-DFE-Client-Id'] == 'am-android-google'
    assert base_headers['X-DFE-MCCMNC'] == '22210'
    assert len(base_headers) == 8


def test_device_builder_get_device_upload_headers(gp_api):
    device_upload_headers = gp_api.deviceBuilder.getDeviceUploadHeaders()
    assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['User-Agent'] == 'Android-Finsky/10.4.13-all [0] [PR] 198917767 (api=3,versionCode=81041300,sdk=27,device=angler,hardware=angler,product=angler,platformVersionRelease=8.1.0,model=Nexus 6P,buildId=OPM2.171019.029.B1,isWideScreen=0,supportedAbis=arm64-v8a;armeabi-v7a;armeabi)'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    # assert device_upload_headers['Accept-Language'] == 'en-US'
    assert len(device_upload_headers) == 12


def test_device_builder_get_user_agent(gp_api):
    user_agent = gp_api.deviceBuilder.getUserAgent()
    assert user_agent == 'Android-Finsky/10.4.13-all [0] [PR] 198917767 (api=3,versionCode=81041300,sdk=27,device=angler,hardware=angler,product=angler,platformVersionRelease=8.1.0,model=Nexus 6P,buildId=OPM2.171019.029.B1,isWideScreen=0,supportedAbis=arm64-v8a;armeabi-v7a;armeabi)'


def test_device_builder_get_auth_headers(gp_api):
    auth_headers = gp_api.deviceBuilder.getAuthHeaders(gsfid=int(config['gp']['gsfid']))
    assert len(auth_headers) == 2
    assert auth_headers['User-Agent'] == 'GoogleAuth/1.4 (angler OPM2.171019.029.B1)'
    assert auth_headers['device'] == '3c0f9b266a920acb'


def test_device_builder_get_login_params(gp_api):
    login_params = gp_api.deviceBuilder.getLoginParams(email=config['gp']['test_email'],
                                                       encrypted_passwd=config['gp']['expected_encrypted_pass'])
    assert len(login_params) == 12
    assert login_params['Email'] == config['gp']['test_email']
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'
    # assert login_params['add_account'] == '1'


def test_device_builder_get_android_checkin_request(gp_api):
    checkin_request = gp_api.deviceBuilder.getAndroidCheckinRequest()
    assert checkin_request.version == 3
    assert checkin_request.id == 0
    assert checkin_request.locale == 'en_US'
    assert checkin_request.timeZone == 'UTC'
    assert checkin_request.version == 3
    assert checkin_request.fragment == 0
    assert checkin_request.checkin != ''


def test_device_builder_get_device_config(gp_api):
    device_config = gp_api.deviceBuilder.getDeviceConfig()
    assert device_config.glEsVersion == 196610
    assert device_config.hasHardKeyboard == False
    assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392
    # assert device_config.screenHeight == 2392


def test_device_builder_get_android_build(gp_api):
    android_build = gp_api.deviceBuilder.getAndroidBuild()
    assert android_build.id == 'google/angler/angler:8.1.0/OPM2.171019.029.A1/4720889:user/release-keys'
    assert android_build.model == 'Nexus 6P'
    assert android_build.sdkVersion == 27
    assert android_build.buildProduct == 'angler'
    assert android_build.googleServices == 12688052


def test_device_builder_get_android_checkin(gp_api):
    android_checkin = gp_api.deviceBuilder.getAndroidCheckin()
    assert android_checkin.cellOperator == '22210'
    assert android_checkin.roaming == 'mobile-notroaming'
    assert android_checkin.simOperator == '22210'
    assert android_checkin.lastCheckinMsec == 0


def test_google_play_login_needs_browser(gp_api):
    try:
        gp_api.login(email=config['gp']['test_email'], password=config['gp']['test_pass'], gsfId=None,
                     authSubToken=None)
    except UnboundLocalError as e:
        assert True
        assert e.args[0] == "local variable 'ac2dmToken' referenced before assignment"


def test_google_play_login_token(gp_api):
    gp_api.login(email=None, password=None, gsfId=config['gp']['gsfid'], authSubToken=config['gp']['authSubToken'])
    assert gp_api.gsfId == config['gp']['gsfid']
    assert gp_api.authSubToken == config['gp']['authSubToken']


def test_google_play_set_auth_sub_token(gp_api):
    gp_api.setAuthSubToken(config['gp']['authSubToken'])
    assert gp_api.authSubToken == config['gp']['authSubToken']


def test_google_play_details(gp_api_logged_in):
    details = gp_api_logged_in.details(config['gp']['package_name_test'])
    assert len(details) == 21
    assert details['docid'] == 'com.postmuseapp.designer'
    assert details['creator'] == 'PostMuse'
    assert details['detailsUrl'] == 'details?doc=com.postmuseapp.designer'


def test_google_play_get_headers(gp_api_logged_in):
    headers = gp_api_logged_in.getHeaders()
    assert len(headers) == 10
    assert headers['Accept-Language'] == 'en-US'
    assert headers['X-DFE-Device-Id'] == '3c0f9b266a920acb'
    assert headers['X-DFE-MCCMNC'] == '22210'


def test_google_play_checkin(gp_api_logged_in):
    checkin = gp_api_logged_in.checkin('test_data', 'test_data')
    assert type(checkin) == int
    assert int(math.log10(checkin)) == 18


def test_google_play_upload_device_config(gp_api_logged_in):
    gp_api_logged_in.uploadDeviceConfig()
    assert type(gp_api_logged_in.device_config_token) is str


def test_google_play_get_second_round_token(gp_api_logged_in):
    try:
        gp_api_logged_in.getSecondRoundToken('data', 'data')
    except TypeError as e:
        assert True
        assert e.args[0] == "'str' object does not support item assignment"


def test_google_play_executeRequestApi2(gp_api_logged_in):
    message = gp_api_logged_in.executeRequestApi2(config['gp']['path_for_execute_api'])
    assert message.payload != ''
    assert message.serverCookies != ''


def test_google_play_download_from_class(gp_api_logged_in):
    response = gp_api_logged_in.download(config['gp']['package_name_test'])
    assert response[1]['developerName'] == 'PostMuse'
    assert response[1]['developerWebsite'] == 'https://postmuseapp.com'


def test_google_play_download_default():
    path_to_file = google_play_download(config['gp']['package_name_test'], None, None,
                                        int(config['gp']['gsfid']), config['gp']['authSubToken'], None, False)
    assert path_to_file != ''


# App Store unit tests
def test_AppStore_class_clean_init():
    appstore = AppStore('appstore_apple_id', 'appstore_password2FA', 'appstore_app_id',
                        'appstore_bundle_id', 'appstore_file_name')
    assert appstore.app_id == 'appstore_app_id'
    assert appstore.apple_id == 'appstore_apple_id'
    assert appstore.pass2FA == 'appstore_password2FA'
    assert appstore.bundle_id == 'appstore_bundle_id'
    assert appstore.appstore_file_name == 'appstore_file_name'
    assert appstore.download_path == 'downloaded_apps'
    assert appstore.app_version == ''
    assert appstore.url == ''


def test_get_zipinfo_datetime():
    zipinfo_time = get_zipinfo_datetime()
    assert type(zipinfo_time) == tuple
    assert zipinfo_time[0] >= 2022
    assert 1 <= zipinfo_time[1] <= 12


def test_store_client_class_init():
    store_client = StoreClient(requests.Session())
    assert store_client.sess != ''
    assert store_client.account_name is None
    assert store_client.guid == '000C2941396B'
    assert store_client.store_front is None
    assert store_client.dsid is None


def test_download_app_appstore_by_id(appstore_logged_in):
    appstore_logged_in.app_id = config['as']['app_id']
    app_path = appstore_logged_in.download_app()
    app_name = "Ростелеком"
    assert app_path != ''
    assert app_name in app_path


def test_download_app_appstore_by_bundle(appstore_logged_in):
    appstore_logged_in.bundle_id = config['as']['bundle_id']
    app_path = appstore_logged_in.download_app()
    app_name = "Газпром"
    assert app_path != ''
    assert app_name in app_path


def test_download_app_appstore_invalid_data(appstore_logged_in):
    try:
        appstore_logged_in.bundle_id = 'app1337'
        appstore_logged_in.download_app()
    except SystemExit:

        assert True


def test_store_client_authenticate():
    store_client = StoreClient(requests.Session())
    auth_resp = store_client.authenticate(config['as']['apple_id'], config['as']['password2FA'])
    assert auth_resp.status == -128
    assert auth_resp.freeSongBalance == '1311811'
    assert auth_resp.dsPersonId == '20279203723'
    assert auth_resp.cancel_purchase_batch is None


def test_store_client_find_app_by_bundle():
    store_client = StoreClient(requests.Session())
    found_app_resp = store_client.find_app_by_bundle(config['as']['bundle_id'])
    app_data = found_app_resp.json()['results'][0]
    assert found_app_resp.status_code == 200
    assert found_app_resp.json()['resultCount'] == 1
    assert app_data['trackName'] == 'Газпромбанк'
    assert app_data['minimumOsVersion'] == '10.3'
    assert app_data['trackId'] == 1406492297


def test_store_client_purchase():
    store_client = StoreClient(requests.Session())
    purchase_resp = store_client.purchase(config['as']['app_id_to_purchase'])
    assert purchase_resp.status_code == 200


def test_store_from_client_download_failure():
    store_client = StoreClient(requests.Session())
    download_from_client_resp = store_client.download('1321')
    assert download_from_client_resp.failureType == '5002'
    assert download_from_client_resp.customerMessage == 'An unknown error has occurred'


# Constants and helpers utils unit tests
def test_dast_state_class_values():
    test_dast_state_class = DastState
    assert test_dast_state_class.CREATED == 0
    assert test_dast_state_class.STARTING == 1
    assert test_dast_state_class.STARTED == 2
    assert test_dast_state_class.ANALYZING == 3
    assert test_dast_state_class.SUCCESS == 4
    assert test_dast_state_class.FAILED == 5
    assert test_dast_state_class.STOPPING == 6
    assert test_dast_state_class.RECALCULATING == 7
    assert test_dast_state_class.INTERRUPTING == 8
    assert test_dast_state_class.INITIALIZING == 9
    assert test_dast_state_class.CANCELLED == 10
    assert test_dast_state_class.CANCELLING == 11


def test_dast_state_dict_values():
    test_dast_state_dict = DastStateDict
    assert test_dast_state_dict[0] == 'CREATED'
    assert test_dast_state_dict[1] == 'STARTING'
    assert test_dast_state_dict[2] == 'STARTED'
    assert test_dast_state_dict[3] == 'ANALYZING'
    assert test_dast_state_dict[4] == 'SUCCESS'
    assert test_dast_state_dict[5] == 'FAILED'
    assert test_dast_state_dict[6] == 'STOPPING'
    assert test_dast_state_dict[7] == 'RECALCULATING'
    assert test_dast_state_dict[8] == 'INTERRUPTING'
    assert test_dast_state_dict[9] == 'INITIALIZING'
    assert test_dast_state_dict[10] == 'CANCELLED'
    assert test_dast_state_dict[11] == 'CANCELLING'


def test_const_values():
    assert TRY_COUNT == 360
    assert END_SCAN_TIMEOUT == 30
    assert SLEEP_TIMEOUT == 10


def test_logger():
    try:
        Log.error('Test error')
        Log.warning('Test warning')
        Log.info('Test info')
        Log.debug('Test debug')
    except Exception as e:
        assert False
    assert True


def test_get_app_path():
    path = get_app_path('test_app.apk')
    assert 'test_app.apk' in path
