from mdast_cli.distribution_systems.google_play import GooglePlayAPI
from mdast_cli.distribution_systems.appstore import AppStore


# Google Play unit tests
def test_Google_play_class_clean_init():
    gp_api = GooglePlayAPI()
    assert gp_api.gsfId is None
    assert gp_api.authSubToken is None
    assert gp_api.device_config_token is None
    assert gp_api.dfeCookie is None
    assert gp_api.deviceCheckinConsistencyToken is None


def test_deviceBuilder_class_clean_init():
    device_builder = GooglePlayAPI().deviceBuilder
    assert device_builder.locale is 'en_US'
    assert device_builder.timezone is 'UTC'


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
    assert len(fake_device_data) is 36


# App Store unit tests
def test_AppStore_class_clean_init():
    appstore = AppStore('appstore_apple_id', 'appstore_password2FA', 'appstore_app_id',
                        'appstore_bundle_id', 'appstore_file_name')
    assert appstore.app_id is 'appstore_app_id'
    assert appstore.apple_id is 'appstore_apple_id'
    assert appstore.pass2FA is 'appstore_password2FA'
    assert appstore.bundle_id is 'appstore_bundle_id'
    assert appstore.appstore_file_name is 'appstore_file_name'
    assert appstore.download_path is 'downloaded_apps'
    assert appstore.app_version is ''
    assert appstore.url is ''
