import argparse
import json
import os
import sys
import time

import urllib3

try:
    from mdast_cli_core import mDastToken as mDast
except (ModuleNotFoundError, ImportError):
    # Export package directory to python environment. Needed for run script without installing package
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

    from mdast_cli_core.token import mDastToken as mDast

try:
    from distribution_systems.app_center import AppCenter
    from distribution_systems.appstore import AppStore
    from distribution_systems.firebase import Firebase
    from distribution_systems.google_play import google_play_download
    from distribution_systems.nexus import NexusRepository
    from helpers.const import END_SCAN_TIMEOUT, SLEEP_TIMEOUT, TRY_COUNT, DastState, DastStateDict
    from helpers.helpers import check_app_md5
    from helpers.logging import Log
except ImportError:
    from mdast_cli.distribution_systems.app_center import AppCenter
    from mdast_cli.distribution_systems.appstore import AppStore
    from mdast_cli.distribution_systems.firebase import Firebase
    from mdast_cli.distribution_systems.google_play import google_play_download
    from mdast_cli.distribution_systems.nexus import NexusRepository
    from mdast_cli.helpers.const import END_SCAN_TIMEOUT, SLEEP_TIMEOUT, TRY_COUNT, DastState, DastStateDict
    from mdast_cli.helpers.helpers import check_app_md5
    from mdast_cli.helpers.logging import Log


def parse_args():
    parser = argparse.ArgumentParser(description='Start scan and get scan results.')
    parser.add_argument('--download_only', '-d', action='store_true', help='Use it for downloading application '
                                                                           'without scan.'
                                                                           ' This argument is optional')
    parser.add_argument('--distribution_system', '-ds', type=str, help='Select how to download file: '
                                                                       'file/appcenter/nexus'
                                                                       '/firebase/appstore/google_play',
                        choices=['file', 'appcenter', 'nexus', 'firebase', 'appstore', 'google_play'],
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
    parser.add_argument('--firebase_project_id', type=str,
                        help='Project id for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_app_id', type=str,
                        help='Application id for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_app_code', type=str,
                        help='Application code for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_api_key', type=str,
                        help='Api code for firebase where mobile application is located.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_SID_cookie', type=str,
                        help='SID cookie for firebase authentication  via google sso.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_HSID_cookie', type=str,
                        help='HSID cookie for firebase authentication  via google sso.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_SSID_cookie', type=str,
                        help='SSID cookie for firebase authentication  via google sso.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_APISID_cookie', type=str,
                        help='APISID cookie for firebase authentication  via google sso.'
                             ' This argument is required if distribution system set to "firebase"')
    parser.add_argument('--firebase_SAPISID_cookie', type=str,
                        help='SAPISID cookie for firebase authentication  via google sso.'
                             ' This argument required if distribution system set to "firebase"')
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
                             'This argument is required if distribution system set to "appstore"')
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
    parser.add_argument('--google_play_file_name', type=str,
                        help='File name for downloaded application.'
                             ' This argument is optional if distribution system set to "google_play"')
    parser.add_argument('--google_play_download_with_creds', action='store_true',
                        help='Download the application at the first login with email + password. '
                             'This argument is optional if distribution system set to "google_play"')

    # Main arguments
    parser.add_argument('--url', type=str, help='System url', required=('-d' == False))
    parser.add_argument('--company_id', type=int, help='Company id for starting scan', required=('-d' == False))
    parser.add_argument('--architecture_id', type=int, help='Architecture id to perform scan', required=('-d' == False))
    parser.add_argument('--token', type=str, help='CI/CD Token for start scan and get results',
                        required=('-d' == False))
    parser.add_argument('--profile_id', type=int, help='Project id for scan', required=('-d' == False))
    parser.add_argument('--testcase_id', type=int, help='Testcase Id')
    parser.add_argument('--summary_report_json_file_name', type=str,
                        help='Name for the json file with summary results in structured format')
    parser.add_argument('--pdf_report_file_name', type=str, help='Name for the pdf report file.')
    parser.add_argument('--nowait', '-nw', action='store_true',
                        help='Wait before scan ends and get results if set to True. If set to False - just start scan '
                             'and exit')

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

    elif args.distribution_system == 'firebase' and (
            args.firebase_project_id is None or
            args.firebase_app_id is None or
            args.firebase_app_code is None or
            args.firebase_api_key is None or
            args.firebase_SID_cookie is None or
            args.firebase_HSID_cookie is None or
            args.firebase_SSID_cookie is None or
            args.firebase_APISID_cookie is None or
            args.firebase_SAPISID_cookie is None or
            args.firebase_file_extension is None):
        parser.error('"--distribution_system nexus" requires "--firebase_project_id", "--firebase_app_id", '
                     '"--firebase_app_code", "--firebase_api_key", "--firebase_api_key", "--firebase_SID_cookie", '
                     '"--firebase_HSID_cookie", "--firebase_SSID_cookie", "--firebase_APISID_cookie", '
                     '"--firebase_SAPISID_cookie", "--firebase_file_extension" arguments to be set')

    elif args.distribution_system == 'appstore' and (
            (args.appstore_app_id is None and args.appstore_bundle_id is None) or
            args.appstore_apple_id is None or
            args.appstore_password2FA is None):
        parser.error('"--distribution_system appstore" requires either "--appstore_app_id" or "--appstore_bundle_id", '
                     '"--appstore_apple_id", "--appstore_password2FA" arguments to be set')

    elif args.distribution_system == 'google_play' and (
            args.google_play_package_name is None or
            ((args.google_play_email is None or args.google_play_password is None) and
             (args.google_play_gsfid is None or args.google_play_auth_token is None))):
        parser.error('"--distribution_system google_play" requires "--google_play_package_name" and either'
                     ' email + pass ("--google_play_email" + "--google_play_password") or '
                     'gsfid + token ("--google_play_gsfid" + "google_play_auth_token") arguments to be set')
    return args


def main():
    urllib3.disable_warnings()

    arguments = parse_args()

    distribution_system = arguments.distribution_system

    if arguments.download_only is False:
        url = arguments.url
        company_id = arguments.company_id
        architecture = arguments.architecture_id
        token = arguments.token
        profile_id = arguments.profile_id
        testcase_id = arguments.testcase_id
        json_summary_file_name = arguments.summary_report_json_file_name
        pdf_report_file_name = arguments.pdf_report_file_name
        not_wait_scan_end = arguments.nowait

        url = url if url.endswith('/') else f'{url}/'
        url = url if url.endswith('rest/') else f'{url}rest'

    app_file = ''
    if distribution_system == 'file':
        app_file = arguments.file_path
    elif distribution_system == 'appcenter':
        appcenter = AppCenter(arguments.appcenter_token,
                              arguments.appcenter_app_name,
                              arguments.appcenter_owner_name,
                              arguments.appcenter_app_version,
                              arguments.appcenter_release_id)
        app_file = appcenter.download_app()
    elif distribution_system == 'nexus':
        nexus_repository = NexusRepository(arguments.nexus_url,
                                           arguments.nexus_login,
                                           arguments.nexus_password,
                                           arguments.nexus_repo_name,
                                           arguments.nexus_group_id,
                                           arguments.nexus_artifact_id,
                                           arguments.nexus_version)
        app_file = nexus_repository.download_app()
    elif distribution_system == 'firebase':
        firebase = Firebase(arguments.firebase_project_id,
                            arguments.firebase_app_id,
                            arguments.firebase_app_code,
                            arguments.firebase_api_key,
                            arguments.firebase_SID_cookie,
                            arguments.firebase_HSID_cookie,
                            arguments.firebase_SSID_cookie,
                            arguments.firebase_APISID_cookie,
                            arguments.firebase_SAPISID_cookie,
                            arguments.firebase_file_extension,
                            arguments.firebase_file_name)
        app_file = firebase.download_app()
    elif distribution_system == 'appstore':
        appstore = AppStore(arguments.appstore_apple_id,
                            arguments.appstore_password2FA,
                            arguments.appstore_app_id,
                            arguments.appstore_bundle_id,
                            arguments.appstore_file_name)
        app_file = appstore.download_app()
    elif distribution_system == 'google_play':
        app_file = google_play_download(arguments.google_play_package_name,
                                        arguments.google_play_email,
                                        arguments.google_play_password,
                                        arguments.google_play_gsfid,
                                        arguments.google_play_auth_token,
                                        arguments.google_play_file_name,
                                        arguments.google_play_download_with_creds)

    if arguments.download_only is True:
        Log.info('Your application was downloaded!')
        sys.exit(0)

    mdast = mDast(url, token, company_id)
    get_architectures_resp = mdast.get_architectures()

    if get_architectures_resp.status_code != 200:
        Log.error('Error while getting architectures.')
        Log.error(f'Server response: {get_architectures_resp.text}')
        sys.exit(1)

    architectures = get_architectures_resp.json()

    if testcase_id is not None:
        get_testcase_resp = mdast.get_testcase(testcase_id)
        if get_testcase_resp.status_code == 200:
            architecture = get_testcase_resp.json()['architecture']['id']
        else:
            Log.warning("Testcase with this id does not exist or you use old version of system. Trying to use "
                        "architecture from command line params.")
        if architecture is not None:
            pass
        else:
            Log.error("No architecture was specified")
            sys.exit(1)

    architecture_type = next(arch for arch in architectures if arch.get('id', '') == architecture)
    if architecture_type is None:
        Log.error("No suitable architecture find for this app")
        sys.exit(1)

    if testcase_id is None:
        Log.info(f'Start manual scan with profile id: {profile_id} and file located in {app_file},'
                 f' architecture id is {architecture}')
    else:
        Log.info(f'Start auto scan with test case Id: '
                 f'{testcase_id}, profile Id: {profile_id} and file: {app_file}, architecture id is {architecture}')

    Log.info('Check if this version of application was already uploaded..')
    check_app_already_uploaded = mdast.check_app_md5(mdast.company_id, check_app_md5(app_file)).json()
    if check_app_already_uploaded:
        application = check_app_already_uploaded[0]
        Log.info(f"This app was uploaded before, application id is: {application['id']}, "
                 f"package name: {application['package_name']},"
                 f" version: {application['version_name']}, md5: {application['md5']}")
    else:
        Log.info('This is new application or new version')
        Log.info('Uploading application to server..')
        upload_application_resp = mdast.upload_application(app_file, str(architecture_type['type']))
        if upload_application_resp.status_code != 201:
            Log.error(f'Error while uploading application to server: {upload_application_resp.text}')
            sys.exit(1)
        application = upload_application_resp.json()
        Log.info(f"Application uploaded successfully. Application id: {application['id']}")

    Log.info(f"Creating scan for application {application['id']}")

    if 'Android' in architecture_type.get('name', ''):
        if not testcase_id:
            create_dast_resp = mdast.create_manual_scan(profile_id=profile_id,
                                                        app_id=application['id'],
                                                        arch_id=architecture)
            scan_type = 'manual'
        else:
            create_dast_resp = mdast.create_auto_scan(profile_id=profile_id,
                                                      app_id=application['id'],
                                                      arch_id=architecture,
                                                      test_case_id=testcase_id)
            scan_type = 'auto'
    elif 'iOS' in architecture_type.get('name', ''):
        create_dast_resp = mdast.create_manual_scan(profile_id=profile_id,
                                                    app_id=application['id'],
                                                    arch_id=architecture)
        scan_type = 'manual'
    else:
        Log.error("Cannot create scan - unknown architecture")
        sys.exit(1)

    if create_dast_resp.status_code != 201:
        Log.error(f'Error while creating scan: {create_dast_resp.text}')
        sys.exit(1)

    dast = create_dast_resp.json()
    if 'id' not in dast and dast.get('id', '') != '':
        Log.error(f'Something went wrong while creating scan: {dast}')
        sys.exit(1)

    if scan_type == 'auto':
        Log.info(f"Autoscan was created successfully. Scan id: {dast['id']}")
    else:
        Log.info(f"Manual scan was created successfully. Scan id: {dast['id']}")

    Log.info(f"Start scan with id {dast['id']}")
    start_dast_resp = mdast.start_scan(dast['id'])
    if start_dast_resp.status_code != 200:
        Log.error(f"Error while starting scan with id {dast['id']}: {start_dast_resp.text}")
        sys.exit(1)

    if not_wait_scan_end:
        Log.info('Scan successfully started. Don`t wait for end, exit with zero code')
        sys.exit(0)

    Log.info("Scan started successfully.")
    Log.info(f"Checking scan state with id {dast['id']}")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)

    dast = get_dast_info_resp.json()
    dast_status = dast['state']
    Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
    count = 0

    while dast_status in (DastState.CREATED, DastState.INITIALIZING, DastState.STARTING) and count < TRY_COUNT:
        Log.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if get_dast_info_resp.status_code != 200:
            Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)

        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        if dast_status not in (DastState.STARTED, DastState.SUCCESS):
            Log.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
            time.sleep(SLEEP_TIMEOUT)

    if dast['state'] not in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING, DastState.SUCCESS):
        Log.error(f"Error with scan id {dast['id']}. Current scan status: {dast['state']},"
                  f" but expected to be {DastState.STARTED}, {DastState.ANALYZING}, {DastState.STOPPING} "
                  f"or {DastState.SUCCESS}")
        sys.exit(1)
    Log.info(f"Scan {dast['id']} is started now. Let's wait until the scan is finished")

    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    count = 0

    while dast_status in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING) and count < TRY_COUNT:
        if count == 0 and scan_type == 'manual':
            if dast_status not in (DastState.ANALYZING, DastState.SUCCESS):
                Log.info(f"This is manual scan with dynamic modules,"
                         f" lets wait for {END_SCAN_TIMEOUT} seconds and stop it.")
                time.sleep(END_SCAN_TIMEOUT)
                stop_manual_dast_resp = mdast.stop_scan(dast['id'])
                if stop_manual_dast_resp.status_code == 200:
                    Log.info(f'Scan {dast["id"]} was successfully stopped')
                else:
                    Log.error(f'Error while stopping scan with id {dast["id"]}: {stop_manual_dast_resp.text}')
                    sys.exit(1)
            else:
                Log.info(f"This is manual scan with profile without dynamic modules,"
                         f" only SAST, lets wait till the end")

        Log.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if get_dast_info_resp.status_code != 200:
            Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)
        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        if dast_status is not DastState.SUCCESS:
            Log.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
            time.sleep(SLEEP_TIMEOUT)

    Log.info(f"Check if scan with id {dast['id']} was finished correctly.")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    dast = get_dast_info_resp.json()

    if dast['state'] != DastState.SUCCESS:
        Log.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)}, but in real it was {dast['state']}. "
            f"Exit with error status code.")
        sys.exit(1)

    if dast['state'] != DastState.SUCCESS:
        Log.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)},"
            f" but in real it was {dast['state']}. Exit with error status code.")
        sys.exit(1)

    if pdf_report_file_name:
        Log.info(f"Create and download pdf report for scan with id {dast['id']} to file {pdf_report_file_name}.")
        pdf_report = mdast.download_report(dast['id'])
        if pdf_report.status_code != 200:
            Log.error(f"PDF report creating failed with error {pdf_report.text}. Exit...")
            sys.exit(1)

        Log.info(f"Saving pdf report to file {pdf_report_file_name}.")
        pdf_report_file_name = pdf_report_file_name if pdf_report_file_name.endswith(
            '.pdf') else f'{pdf_report_file_name}.pdf'
        with open(pdf_report_file_name, 'wb') as f:
            f.write(pdf_report.content)

        Log.info(f"Report for scan {dast['id']} successfully created and available at path: {pdf_report_file_name}.")

    if json_summary_file_name:
        Log.info(
            f"Create and download JSON summary report for scan with id {dast['id']} to file {json_summary_file_name}.")
        json_summary_report = mdast.get_scan_info(dast['id'])
        if json_summary_report.status_code != 200:
            Log.error(f"JSON summary report creating failed with error {json_summary_report.text}. Exit...")
            sys.exit(1)

        Log.info(f"Saving summary json results to file {json_summary_file_name}.")
        mdast_json_file = json_summary_file_name if json_summary_file_name.endswith(
            '.json') else f'{json_summary_file_name}.json'
        with open(mdast_json_file, 'w') as fp:
            json.dump(json_summary_report.json(), fp, indent=4, ensure_ascii=False)

        Log.info(f"JSON report for scan {dast['id']} successfully created and available at path: {mdast_json_file}.")

    Log.info('Job completed successfully!')


if __name__ == '__main__':
    main()
