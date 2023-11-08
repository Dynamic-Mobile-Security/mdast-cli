import argparse
import json
import logging
import os
import sys
import time

import urllib3

from mdast_cli.distribution_systems.app_center import AppCenter
from mdast_cli.distribution_systems.appgallery import appgallery_download_app
from mdast_cli.distribution_systems.appstore import AppStore
from mdast_cli.distribution_systems.firebase import firebase_download_app
from mdast_cli.distribution_systems.google_play import GooglePlay
from mdast_cli.distribution_systems.nexus import NexusRepository
from mdast_cli.distribution_systems.nexus2 import Nexus2Repository
from mdast_cli.distribution_systems.rumarket import rumarket_download_app
from mdast_cli.distribution_systems.rustore import rustore_download_app
from mdast_cli.helpers.const import (ANDROID_EXTENSIONS, END_SCAN_TIMEOUT, LONG_TRY, SLEEP_TIMEOUT, TRY, DastState,
                                     DastStateDict)
from mdast_cli.helpers.helpers import check_app_md5
from mdast_cli_core.token import mDastToken as mDast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S', stream=sys.stdout)

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Start scan and get scan results.')
    parser.add_argument('--download_only', '-d', action='store_true', help='Use it for downloading application '
                                                                           'without scan.'
                                                                           ' This argument is optional')
    parser.add_argument('--distribution_system', '-ds', type=str, help='Select how to download file: '
                                                                       'file/appcenter/nexus/firebase/'
                                                                       'appstore/google_play/rustore/rumarket',
                        choices=['file', 'appcenter', 'nexus', 'nexus2', 'firebase', 'appstore', 'google_play',
                                 'rustore', 'appgallery', 'rumarket'],
                        required=True)

    # Arguments used for distribution_system = file
    parser.add_argument('--file_path', type=str, help='Path to local file for analyze. This argument is required if '
                                                      'distribution system set to "file"')

    # Arguments used for distribution_system appcenter
    parser.add_argument('--appcenter_token', type=str, help='Auth token for AppCenter. This argument is required if '
                                                            'distribution system set to "appcenter"')
    parser.add_argument('--appcenter_owner_name', type=str, help='Application owner name in AppCenter. This argument '
                                                                 'is required if distribution system set'
                                                                 ' to "appcenter"')
    parser.add_argument('--appcenter_app_name', type=str,
                        help='Application name in AppCenter. This argument is required '
                             'if distribution system set to "appcenter"')
    parser.add_argument('--appcenter_release_id', type=str, help='Release id in AppCenter. If not set - the latest '
                                                                 'release will be downloaded. This argument or '
                                                                 '"--ac_app_version" is required if distribution system'
                                                                 ' set to "appcenter"')
    parser.add_argument('--appcenter_app_version', type=str, help='Application version in AppCenter. This argument or '
                                                                  '"--appcenter_release_id" is required if distribution'
                                                                  ' system set to "appcenter"')

    # Arguments for Nexus
    parser.add_argument('--nexus_url', type=str,
                        help='Http url for Nexus server where mobile application is located.'
                             ' This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_login', type=str,
                        help='Login for Nexus server where mobile application is located.'
                             ' This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_password', type=str,
                        help='Password for Nexus server where mobile application is located.'
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_repo_name', type=str,
                        help='Repository name in Nexus where mobile application is located. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_group_id', type=str,
                        help='Group_id for mobile application. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_artifact_id', type=str,
                        help='Artifact id for mobile application. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_version', type=str,
                        help='Version to download from Nexus. '
                             'This argument is required if distribution system set to "appcenter"')

    # Arguments for Firebase
    parser.add_argument('--firebase_project_number', type=int,
                        help='Project number for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_app_id', type=str,
                        help='Application id for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_account_json_path', type=str,
                        help='json.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_file_extension', type=str,
                        help='File extension(apk or ipa) for downloaded application.'
                             ' This argument is required if distribution system set to "firebase"',
                        choices=['ipa', 'apk'])
    parser.add_argument('--firebase_file_name', type=str,
                        help='File name for downloaded application.'
                             ' This argument is optional if distribution system set to "firebase"')

    # Arguments for AppStore
    parser.add_argument('--appstore_app_id', type=str,
                        help='Application id from AppStore, you can get it on app page from url, format: .../id{APP_ID}'
                             'You should specify either bundle_id or app_id if distribution system set to "appstore"')
    parser.add_argument('--appstore_bundle_id', type=str,
                        help='Bundle id of application id from AppStore.'
                             ' You should specify either bundle_id or app_id if distribution system set to "appstore"')
    parser.add_argument('--appstore_apple_id', type=str,
                        help='Your email for iTunes login. This argument is required '
                             'if distribution system set to "appstore"')
    parser.add_argument('--appstore_password2FA', type=str,
                        help='Your password and 2FA code for iTunes login, format: password2FA_code (password1337)'
                             'DEPRECATED, will be deleted on 01.05.2023')
    parser.add_argument('--appstore_password', type=str,
                        help='Your password for iTunes login. This argument is required '
                             'if distribution system set to "appstore"')
    parser.add_argument('--appstore_2FA', type=str, help='Your 2FA code for iTunes login(6 numbers). '
                                                         'This argument is required '
                                                         'if distribution system set to "appstore"')
    parser.add_argument('--appstore_file_name', type=str,
                        help='File name for downloaded application.'
                             ' This argument is optional if distribution system set to "appstore"')

    # Arguments for Google Play
    parser.add_argument('--google_play_package_name', type=str,
                        help='Application package name from Google Play. This argument is required for first login if '
                             'distribution system set to "google_play"')
    parser.add_argument('--google_play_email', type=str,
                        help='Your email for Google Play login. This argument is required for first login if '
                             'distribution system set to "google_play"')
    parser.add_argument('--google_play_password', type=str,
                        help='Your password for Google Play login. This argument is required for first login if'
                             'distribution system set to "google_play"')
    parser.add_argument('--google_play_gsfid', type=int,
                        help='The Google Services Framework Identifier (GSF ID) is a unique 16 character hexadecimal '
                             'number of your fake device. You should get it from console logs during '
                             'first login attempt with email and password.This argument required if '
                             'distribution system set to "google_play"')
    parser.add_argument('--google_play_auth_token', type=str,
                        help='Google auth token for access to Google Play API. '
                             'You should get it from console logs during first login attempt with email and password.'
                             ' This argument required if distribution system set to "google_play"')
    parser.add_argument('--google_play_vc_null', action='store_true', default=None,
                        help='Google play app version code = '', optional, use if DF-DFERH-01 when vc=None ')
    parser.add_argument('--google_play_file_name', type=str,
                        help='File name for downloaded application.'
                             ' This argument is optional if distribution system set to "google_play"')
    parser.add_argument('--google_play_download_with_creds', action='store_true',
                        help='Download the application at the first login with email + password. '
                             'This argument is optional if distribution system set to "google_play"')

    # Arguments for Rustore
    parser.add_argument('--rustore_package_name', type=str,
                        help='Application package name from Rustore. This argument is required if '
                             'distribution system set to "rustore"')

    # Arguments for Rustore
    parser.add_argument('--rumarket_package_name', type=str,
                        help='Application package name from Rumarket. This argument is required if '
                             'distribution system set to "rumarket"')

    # Arguments for Appgallery
    parser.add_argument('--appgallery_app_id', type=str,
                        help='Application id from Appgallery. This argument is required if '
                             'distribution system set to "appgallery".'
                             ' You can get it on app page from url, format: .../id{APP_ID}. example: C13371337')
    parser.add_argument('--appgallery_file_name', type=str,
                        help='File name for downloaded application.'
                             ' This argument is optional if distribution system set to "appgallery"')

    # Arguments for Nexus2
    parser.add_argument('--nexus2_url', type=str,
                        help='Http url for Nexus server where mobile application is located.'
                             ' This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_login', type=str,
                        help='Login for Nexus server where mobile application is located.'
                             ' This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_password', type=str,
                        help='Password for Nexus server where mobile application is located.'
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_repo_name', type=str,
                        help='Repository name in Nexus where mobile application is located. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_group_id', type=str,
                        help='Group_id for mobile application. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_artifact_id', type=str,
                        help='Artifact id for mobile application. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_version', type=str,
                        help='Version to download from Nexus. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_extension', type=str,
                        help='File extension. '
                             'This argument is required if distribution system set to "appcenter"')
    parser.add_argument('--nexus2_file_name', type=str,
                        help='File name to be saved as. '
                             'This argument is optional if distribution system set to "appcenter"')

    # Main arguments
    parser.add_argument('--url', type=str, help='System url', required=(not '-d'))
    parser.add_argument('--company_id', type=int, help='Company id for starting scan', required=(not '-d'))
    parser.add_argument('--token', type=str, help='CI/CD Token for start scan and get results', required=(not '-d'))
    parser.add_argument('--architecture_id', type=int, help='Architecture id to perform scan')
    parser.add_argument('--profile_id', type=int, default=None,
                        help='Profile id for scan. If not set - autocreate profile')
    parser.add_argument('--project_id', type=int, default=None,
                        help='Project id for scan. Only if you want to autocreate profile in existing project')
    parser.add_argument('--testcase_id', type=int, help='Testcase id. If not set - manual scan')
    parser.add_argument('--appium_script_path', type=str, help='Appium script path for autoscan with Stingray appium')
    parser.add_argument('--summary_report_json_file_name', type=str,
                        help='Name for the json file with summary results in structured format')
    parser.add_argument('--pdf_report_file_name', type=str, help='Name for the pdf report file.')
    parser.add_argument('--nowait', '-nw', action='store_true',
                        help='Wait before scan ends and get results if set to True. If set to False - just start scan '
                             'and exit')
    parser.add_argument('--download_path', '-p', type=str, help='Path to folder with downloaded apps',
                        default='downloaded_apps')
    parser.add_argument('--long_wait', action='store_true', help='Time limit - 1 week for scan finish')

    args = parser.parse_args()

    if args.distribution_system == 'file' and args.file_path is None:
        parser.error('"--distribution_system file" requires "--file_path" argument to be set')
    elif args.distribution_system == 'appcenter' and (
            args.appcenter_token is None or
            args.appcenter_owner_name is None or
            args.appcenter_app_name is None or
            (args.appcenter_release_id is None and args.appcenter_app_version is None)):
        parser.error(
            '"--distribution_system appcenter" requires "--appcenter_token", "--appcenter_owner_name",  '
            '"--appcenter_app_name" and '
            '"--appcenter_release_id" or "--appcenter_app_version" arguments to be set')

    elif args.distribution_system == 'nexus' and (
            args.nexus_url is None or
            args.nexus_login is None or
            args.nexus_password is None or
            args.nexus_repo_name is None or
            args.nexus_group_id is None or
            args.nexus_artifact_id is None or
            args.nexus_version is None):
        parser.error('"--distribution_system nexus" requires "--nexus_url", "--nexus_login", "--nexus_password",'
                     ' "--nexus_repo_name" arguments to be set')

    elif args.distribution_system == 'nexus2' and (
            args.nexus2_url is None or
            args.nexus2_login is None or
            args.nexus2_password is None or
            args.nexus2_repo_name is None or
            args.nexus2_group_id is None or
            args.nexus2_artifact_id is None or
            args.nexus2_version is None or
            args.nexus2_extension is None):
        parser.error('"--distribution_system nexus2" requires "--nexus2_url", "--nexus2_login", "--nexus2_password",'
                     ' "--nexus2_repo_name", "--nexus2_group_id", "--nexus2_artifact_id", "--nexus2_extension" '
                     'arguments to be set')

    elif args.distribution_system == 'firebase' and (
            args.firebase_project_number is None or
            args.firebase_app_id is None or
            args.firebase_account_json_path is None or
            args.firebase_file_extension is None):
        parser.error('"--distribution_system firebase" requires "--firebase_project_number", "--firebase_app_id", '
                     '"--firebase_account_json_path", "--firebase_file_extension" arguments to be set')

    elif args.distribution_system == 'appstore' and (
            (args.appstore_app_id is None and args.appstore_bundle_id is None) or
            args.appstore_apple_id is None or
            (args.appstore_password is None or args.appstore_2FA is None) and args.appstore_password2FA is None):
        parser.error('"--distribution_system appstore" requires either "--appstore_app_id" or "--appstore_bundle_id", '
                     '"--appstore_apple_id" and ("--appstore_password" + "--appstore_2FA")/'
                     '(deprecated "--appstore_password2FA") arguments to be set')

    elif args.distribution_system == 'google_play' and (
            args.google_play_package_name is None or
            ((args.google_play_email is None or args.google_play_password is None) and
             (args.google_play_gsfid is None or args.google_play_auth_token is None))):
        parser.error('"--distribution_system google_play" requires "--google_play_package_name" and either'
                     ' email + pass ("--google_play_email" + "--google_play_password") or '
                     'gsfid + token ("--google_play_gsfid" + "google_play_auth_token") arguments to be set')

    elif args.distribution_system == 'rustore' and args.rustore_package_name is None:
        parser.error('"--distribution_system rustore" requires "--rustore_package_name" to be set')

    elif args.distribution_system == 'rumarket' and args.rumarket_package_name is None:
        parser.error('"--distribution_system rumarket" requires "--rumarket_package_name" to be set')

    elif args.distribution_system == 'appgallery' and args.appgallery_app_id is None:
        parser.error('"--distribution_system appgallery" requires "--appgallery_app_id" to be set')

    return args


def main():
    urllib3.disable_warnings()

    arguments = parse_args()

    distribution_system = arguments.distribution_system
    download_path = arguments.download_path

    if arguments.download_only is False:
        url = arguments.url
        company_id = arguments.company_id
        architecture = arguments.architecture_id
        token = arguments.token
        profile_id = arguments.profile_id
        project_id = arguments.project_id
        testcase_id = arguments.testcase_id
        appium_script_path = arguments.appium_script_path
        json_summary_file_name = arguments.summary_report_json_file_name
        pdf_report_file_name = arguments.pdf_report_file_name
        not_wait_scan_end = arguments.nowait
        long_wait = arguments.long_wait

        url = url if url.endswith('/') else f'{url}/'
        url = url if url.endswith('rest/') else f'{url}rest'

    app_file = ''
    appstore_app_md5 = None

    try:
        if distribution_system == 'file':
            app_file = arguments.file_path

        elif distribution_system == 'appcenter':
            appcenter = AppCenter(arguments.appcenter_token)
            app_file = appcenter.download_app(download_path,
                                              arguments.appcenter_owner_name,
                                              arguments.appcenter_app_name,
                                              arguments.appcenter_app_version,
                                              arguments.appcenter_release_id)

        elif distribution_system == 'nexus':
            nexus_repository = NexusRepository(arguments.nexus_url,
                                               arguments.nexus_login,
                                               arguments.nexus_password)
            app_file = nexus_repository.download_app(download_path,
                                                     arguments.nexus_repo_name,
                                                     arguments.nexus_group_id,
                                                     arguments.nexus_artifact_id,
                                                     arguments.nexus_version)
        elif distribution_system == 'nexus2':
            nexus2_repository = Nexus2Repository(arguments.nexus2_url,
                                                 arguments.nexus2_login,
                                                 arguments.nexus2_password)
            app_file = nexus2_repository.download_app(download_path,
                                                      arguments.nexus2_repo_name,
                                                      arguments.nexus2_group_id,
                                                      arguments.nexus2_artifact_id,
                                                      arguments.nexus2_version,
                                                      arguments.nexus2_extension,
                                                      arguments.nexus2_file_name)

        elif distribution_system == 'firebase':
            app_file = firebase_download_app(download_path,
                                             arguments.firebase_project_number,
                                             arguments.firebase_app_id,
                                             arguments.firebase_account_json_path,
                                             arguments.firebase_file_name,
                                             arguments.firebase_file_extension)

        elif distribution_system == 'appstore':
            if arguments.appstore_password and arguments.appstore_2FA:
                password2FA = arguments.appstore_password + arguments.appstore_2FA
            else:
                password2FA = arguments.appstore_password2FA
            appstore = AppStore(arguments.appstore_apple_id,
                                password2FA)
            app_file, appstore_app_md5 = appstore.download_app(download_path,
                                                               arguments.appstore_app_id,
                                                               arguments.appstore_bundle_id,
                                                               arguments.appstore_file_name)

        elif distribution_system == 'google_play':
            google_play = GooglePlay(arguments.google_play_email,
                                     arguments.google_play_password,
                                     arguments.google_play_gsfid,
                                     arguments.google_play_auth_token)
            google_play.login()
            if arguments.google_play_email and arguments.google_play_password \
                    and not arguments.google_play_download_with_creds:
                exit(0)  # just get token and exit

            app_file = google_play.download_app(download_path,
                                                arguments.google_play_package_name, arguments.google_play_vc_null,
                                                arguments.google_play_file_name)

        elif distribution_system == 'rustore':
            package_name = arguments.rustore_package_name
            app_file = rustore_download_app(package_name, download_path)

        elif distribution_system == 'rumarket':
            package_name = arguments.rumarket_package_name
            app_file = rumarket_download_app(package_name, download_path)

        elif distribution_system == 'appgallery':
            app_file = appgallery_download_app(arguments.appgallery_app_id,
                                               download_path,
                                               arguments.appgallery_file_name)

    except Exception as e:
        logger.fatal(f'Cannot download application file: {e}')
        exit(4)

    if arguments.download_only is True:
        logger.info('Your application was downloaded!')
        sys.exit(0)

    mdast = mDast(url, token, company_id)
    get_architectures_resp = mdast.get_architectures()

    if get_architectures_resp.status_code != 200:
        logger.error(f'Error while getting architectures. Server response: {get_architectures_resp.text}')
        sys.exit(1)

    architectures = get_architectures_resp.json()

    _, file_extension = os.path.splitext(app_file)

    if architecture is None:
        if file_extension in ANDROID_EXTENSIONS:
            architecture = next(arch['id'] for arch in architectures if arch.get('name', '') == 'Android 11')
        if file_extension == '.ipa':
            architecture = next(arch['id'] for arch in architectures if arch.get('name', '') == 'iOS 14')
        if architecture is None:
            logger.error("Cannot create scan - no suitable architecture fot this app, try to set it manually")
            sys.exit(1)
    architecture_type = next(arch for arch in architectures if arch.get('id', '') == architecture)
    logger.info(f'Architecture type is {architecture_type}')

    if testcase_id is not None:
        get_testcase_resp = mdast.get_testcase(testcase_id)
        if get_testcase_resp.status_code == 200:
            architecture = get_testcase_resp.json()['architecture']['id']
        else:
            logger.warning("Testcase with this id does not exist or you use old version of system. Trying to use "
                           "architecture from command line params.")

    if sum(e['architecture'] == architecture_type['id'] and e['state'] == 3 for e in mdast.get_engines().json()) == 0:
        logger.error(f"Cannot create scan - Cannot find active engine for architecture {architecture_type['name']}")
        sys.exit(1)

    if testcase_id:
        logger.info(f'Autoscan(Stingray) with test case id: '
                    f'{testcase_id}, profile id: {profile_id} and file: {app_file}, architecture id is {architecture}')
    elif appium_script_path:
        logger.info(f'Autoscan(Appium) with  profile id: {profile_id} and file: {app_file},'
                    f' architecture id is {architecture}')
    else:
        logger.info(f'Manual scan with profile id: {profile_id} and file located in {app_file},'
                    f' architecture id is {architecture}')

    logger.info('Check if this version of application was already uploaded..')
    if appstore_app_md5:
        check_app_already_uploaded = mdast.check_app_md5(mdast.company_id, appstore_app_md5).json()
    else:
        check_app_already_uploaded = mdast.check_app_md5(mdast.company_id, check_app_md5(app_file)).json()
    if check_app_already_uploaded:
        application = check_app_already_uploaded[0]
        logger.info(f"This app was uploaded before, application id is: {application['id']}, "
                    f"package name: {application['package_name']},"
                    f" version: {application['version_name']}, md5: {application['md5']}")
    else:
        logger.info('This is new application or new version')
        logger.info('Uploading application to server..')
        upload_application_resp = mdast.upload_application(app_file, str(architecture_type['type']))
        if upload_application_resp.status_code != 201:
            logger.error(f'Error while uploading application to server: {upload_application_resp.text}')
            sys.exit(1)
        application = upload_application_resp.json()
        logger.info(f"Application uploaded successfully. Application id: {application['id']}")

    logger.info(f"Creating scan for application {application['id']}")
    if testcase_id is not None:
        create_dast_resp = mdast.create_auto_scan(project_id, profile_id, application['id'], architecture, testcase_id)
        scan_type = 'auto_stingray'
    elif appium_script_path is not None:
        create_dast_resp = mdast.create_appium_scan(project_id, profile_id, application['id'], architecture,
                                                    appium_script_path)
        scan_type = 'auto_appium'
    else:
        create_dast_resp = mdast.create_manual_scan(project_id, profile_id, application['id'], architecture)
        scan_type = 'manual'
    if create_dast_resp.status_code != 201:
        logger.error(f'Error while creating scan: {create_dast_resp.text}')
        sys.exit(1)

    dast_info = create_dast_resp.json()
    logger.info(f"Project and profile was created/found successfully."
                f" Project id: {dast_info['project']['id']}, profile id: {dast_info['profile']['id']}")

    dast = create_dast_resp.json()
    if 'id' not in dast and dast.get('id', '') != '':
        logger.error(f'Something went wrong while creating scan: {dast}')
        sys.exit(1)

    if scan_type == 'auto_stingray':
        logger.info(f"Autoscan(Stingray) was created successfully. Scan id: {dast['id']}")
    elif scan_type == 'auto_appium':
        logger.info(f"Autoscan(Appium) was created successfully. Scan id: {dast['id']}")
    else:
        logger.info(f"Manual scan was created successfully. Scan id: {dast['id']}")

    logger.info(f"Start scan with id {dast['id']}")
    start_dast_resp = mdast.start_scan(dast['id'])
    if start_dast_resp.status_code != 200:
        logger.error(f"Error while starting scan with id {dast['id']}: {start_dast_resp.text}")
        sys.exit(1)

    if not_wait_scan_end:
        logger.info('Scan successfully started. Don`t wait for end, exit with zero code')
        sys.exit(0)

    logger.info("Scan started successfully.")
    logger.info(f"Checking scan state with id {dast['id']}")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)

    dast = get_dast_info_resp.json()
    dast_status = dast['state']
    logger.info(f"Current scan status: {DastStateDict.get(dast_status)}")
    count = 0

    if long_wait:
        try_count = LONG_TRY
    else:
        try_count = TRY

    while dast_status in (DastState.CREATED, DastState.INITIALIZING, DastState.STARTING) and count < try_count:
        logger.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if get_dast_info_resp.status_code != 200:
            logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)

        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        logger.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        if dast_status not in (DastState.STARTED, DastState.SUCCESS):
            logger.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
            time.sleep(SLEEP_TIMEOUT)

    if dast['state'] not in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING, DastState.SUCCESS):
        logger.error(f"Error with scan id {dast['id']}. Current scan status: {dast['state']},"
                     f" but expected to be {DastState.STARTED}, {DastState.ANALYZING}, {DastState.STOPPING} "
                     f"or {DastState.SUCCESS}")
        sys.exit(1)
    logger.info(f"Scan {dast['id']} is started now. Let's wait until the scan is finished")

    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    count = 0

    while dast_status in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING) and count < try_count:
        if count == 0 and scan_type == 'manual':
            if dast_status not in (DastState.ANALYZING, DastState.SUCCESS):
                logger.info(f"This is manual scan with dynamic modules,"
                            f" lets wait for {END_SCAN_TIMEOUT} seconds and stop it.")
                time.sleep(END_SCAN_TIMEOUT)
                stop_manual_dast_resp = mdast.stop_scan(dast['id'])
                if stop_manual_dast_resp.status_code == 200:
                    logger.info(f'Scan {dast["id"]} was successfully stopped')
                else:
                    logger.error(f'Error while stopping scan with id {dast["id"]}: {stop_manual_dast_resp.text}')
                    sys.exit(1)
            else:
                logger.info("This is manual scan with profile without dynamic modules,"
                            " only SAST, lets wait till the end")

        logger.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if get_dast_info_resp.status_code != 200:
            logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)
        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        logger.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        if dast_status is not DastState.SUCCESS:
            logger.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
            time.sleep(SLEEP_TIMEOUT)

    logger.info(f"Check if scan with id {dast['id']} was finished correctly.")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    dast = get_dast_info_resp.json()

    if dast['state'] != DastState.SUCCESS:
        logger.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)}, but in real it was {dast['state']}. "
            f"Exit with error status code.")
        sys.exit(1)

    if dast['state'] != DastState.SUCCESS:
        logger.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)},"
            f" but in real it was {dast['state']}. Exit with error status code.")
        sys.exit(1)

    if pdf_report_file_name:
        logger.info(f"Create and download pdf report for scan with id {dast['id']} to file {pdf_report_file_name}.")
        pdf_report = mdast.download_report(dast['id'])
        if pdf_report.status_code != 200:
            logger.error(f"PDF report creating failed with error {pdf_report.text}. Exit...")
            sys.exit(1)

        logger.info(f"Saving pdf report to file {pdf_report_file_name}.")
        pdf_report_file_name = pdf_report_file_name if pdf_report_file_name.endswith(
            '.pdf') else f'{pdf_report_file_name}.pdf'
        with open(pdf_report_file_name, 'wb') as f:
            f.write(pdf_report.content)

        logger.info(f"Report for scan {dast['id']} successfully created and available at path: {pdf_report_file_name}.")

    if json_summary_file_name:
        logger.info(
            f"Download JSON summary report for scan with id {dast['id']} to file {json_summary_file_name}.")
        json_summary_report = mdast.download_scan_json_result(dast['id'])
        if json_summary_report.status_code != 200:
            logger.error(f"JSON summary report while downloading failed with error {json_summary_report.text}. Exit...")
            sys.exit(1)

        logger.info(f"Saving summary json results to file {json_summary_file_name}.")
        mdast_json_file = json_summary_file_name if json_summary_file_name.endswith(
            '.json') else f'{json_summary_file_name}.json'
        with open(mdast_json_file, 'w') as fp:
            json.dump(json_summary_report.json(), fp, indent=4, ensure_ascii=False)

        logger.info(f"JSON report for scan {dast['id']} successfully created and available at path: {mdast_json_file}.")

    logger.info('Job completed successfully!')


if __name__ == '__main__':
    main()
