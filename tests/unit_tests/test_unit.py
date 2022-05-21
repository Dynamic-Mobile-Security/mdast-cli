from pytest_testconfig import config

from mdast_cli.distribution_systems.google_play import GooglePlayAPI
from mdast_cli.distribution_systems.appstore import AppStore
from mdast_cli.distribution_systems.gpapi.googleplay import encrypt_password
from mdast_cli.distribution_systems.gpapi.config import DeviceBuilder

from mdast_cli.helpers.const import *


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
    # assert fake_device_data['build.version.sdk_int'] == '27'
    # assert fake_device_data['build.version.release'] == '8.1.0'
    # assert fake_device_data['gsf.version'] == '12688052'
    # assert fake_device_data['timezone'] == 'America/Los_Angeles'
    # assert fake_device_data['client'] == 'android-google'
    # assert fake_device_data['build.product'] == 'angler'
    # assert fake_device_data['build.id'] == 'OPM2.171019.029.B1'
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


def test_device_builder_init():
    gp_api = GooglePlayAPI()
    device_builder = gp_api.deviceBuilder
    assert device_builder.locale == 'en_US'
    assert device_builder.timezone == 'UTC'
    assert type(device_builder.device) == dict
    assert len(device_builder.device) == 36


def test_device_builder_set_locale():
    gp_api = GooglePlayAPI()
    gp_api.deviceBuilder.setLocale('test_locale')
    assert gp_api.deviceBuilder.locale == 'test_locale'


def test_device_builder_set_invalid_locale():
    gp_api = GooglePlayAPI()
    current_locale = gp_api.deviceBuilder.locale
    try:
        gp_api.deviceBuilder.setLocale('')
    except ValueError as e:
        assert True
        assert e.args[0] == 'locale is not defined'
    assert gp_api.deviceBuilder.locale != ''
    assert gp_api.deviceBuilder.locale == current_locale


def test_device_builder_set_timezone():
    gp_api = GooglePlayAPI()
    gp_api.deviceBuilder.setTimezone('test_timezone')
    assert gp_api.deviceBuilder.timezone == 'test_timezone'


def test_device_builder_get_base_headers():
    gp_api = GooglePlayAPI()
    base_headers = gp_api.deviceBuilder.getBaseHeaders()
    assert base_headers['Accept-Language'] == 'en-US'
    # assert base_headers['Accept-Language'] == 'en-US'
    # assert base_headers['Accept-Language'] == 'en-US'
    # assert base_headers['Accept-Language'] == 'en-US'
    # assert base_headers['Accept-Language'] == 'en-US'
    # assert base_headers['Accept-Language'] == 'en-US'
    assert len(base_headers) == 8


def test_device_builder_get_device_upload_headers():
    gp_api = GooglePlayAPI()
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


def test_device_builder_get_user_agent():
    gp_api = GooglePlayAPI()
    user_agent = gp_api.deviceBuilder.getUserAgent()
    assert user_agent == 'Android-Finsky/10.4.13-all [0] [PR] 198917767 (api=3,versionCode=81041300,sdk=27,device=angler,hardware=angler,product=angler,platformVersionRelease=8.1.0,model=Nexus 6P,buildId=OPM2.171019.029.B1,isWideScreen=0,supportedAbis=arm64-v8a;armeabi-v7a;armeabi)'


def test_device_builder_get_auth_headers():
    gp_api = GooglePlayAPI()
    auth_headers = gp_api.deviceBuilder.getAuthHeaders(gsfid=int(config['gp']['gsfid']))
    assert len(auth_headers) == 2
    assert auth_headers['User-Agent'] == 'GoogleAuth/1.4 (angler OPM2.171019.029.B1)'
    assert auth_headers['device'] == '3c0f9b266a920acb'


def test_device_builder_get_login_params():
    gp_api = GooglePlayAPI()
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


def test_device_builder_get_android_checkin_request():
    gp_api = GooglePlayAPI()
    checkin_request = gp_api.deviceBuilder.getAndroidCheckinRequest()
    assert checkin_request.version == 3
    assert checkin_request.id == 0
    assert checkin_request.locale == 'en_US'
    assert checkin_request.timeZone == 'UTC'
    assert checkin_request.version == 3
    assert checkin_request.fragment == 0
    assert checkin_request.checkin != ''


def test_device_builder_get_device_config():
    gp_api = GooglePlayAPI()
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


def test_device_builder_get_android_build():
    gp_api = GooglePlayAPI()
    android_build = gp_api.deviceBuilder.getAndroidBuild()
    assert android_build.id == 'google/angler/angler:8.1.0/OPM2.171019.029.A1/4720889:user/release-keys'
    assert android_build.model == 'Nexus 6P'
    assert android_build.sdkVersion == 27
    assert android_build.buildProduct == 'angler'
    assert android_build.googleServices == 12688052
    # assert android_build.googleServices == 12688052
    # assert android_build.googleServices == 12688052
    # assert android_build.googleServices == 12688052


def test_device_builder_get_android_checkin():
    gp_api = GooglePlayAPI()
    android_checkin = gp_api.deviceBuilder.getAndroidCheckin()
    assert android_checkin.cellOperator == '22210'
    assert android_checkin.roaming == 'mobile-notroaming'
    assert android_checkin.simOperator == '22210'
    assert android_checkin.lastCheckinMsec == 0


def test_google_play_download():
    pass


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


# Constants unit tests
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


# def test_dast_state_dict_values():
#     test_dast_state_dict = DastStateDict
#     assert test_dast_state_dict['CREATED'] == 0
#     assert test_dast_state_dict['STARTING'] == 1
#     assert test_dast_state_dict['STARTED'] == 2
#     assert test_dast_state_dict['ANALYZING'] == 3
#     assert test_dast_state_dict['SUCCESS'] == 4
#     assert test_dast_state_dict['FAILED'] == 5
#     assert test_dast_state_dict['STOPPING'] == 6
#     assert test_dast_state_dict['RECALCULATING'] == 7
#     assert test_dast_state_dict['INTERRUPTING'] == 8
#     assert test_dast_state_dict['INITIALIZING'] == 9
#     assert test_dast_state_dict['CANCELLED'] == 10
#     assert test_dast_state_dict['CANCELLING'] == 11


def test_const_values():
    pass