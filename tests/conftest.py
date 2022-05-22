from pytest_testconfig import config
import pytest
from mdast_cli.distribution_systems.google_play import GooglePlayAPI
from mdast_cli.distribution_systems.appstore import AppStore


@pytest.fixture
def gp_api():
    gp_api = GooglePlayAPI()
    return gp_api


@pytest.fixture(scope="session")
def gp_api_logged_in():
    gsfId = config['gp']['gsfid']
    auth_token = config['gp']['authSubToken']
    gp_api = GooglePlayAPI()
    gp_api.login(email=None, password=None, gsfId=int(gsfId), authSubToken=auth_token)
    return gp_api


@pytest.fixture
def appstore_logged_in():
    appstore = AppStore(config['as']['apple_id'], config['as']['password2FA'])
    return appstore
