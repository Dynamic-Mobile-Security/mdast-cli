import sys
import time
import json
import urllib3
import argparse
import os

try:
    from mdast_cli_core import mDastToken as mDast
except (ModuleNotFoundError, ImportError):
    # Export package directory to python environment. Needed for run script without installing package
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

    from mdast_cli_core.token import mDastToken as mDast

try:
    from .helpers.const import *
    from .helpers.logging import Log
    from .distribution_systems.hockey_app import HockeyApp
    from .distribution_systems.app_center import AppCenter
    from .distribution_systems.nexus import NexusRepository
except ImportError:
    from mdast_cli.helpers.const import *
    from mdast_cli.helpers.logging import Log
    from mdast_cli.distribution_systems.hockey_app import HockeyApp
    from mdast_cli.distribution_systems.app_center import AppCenter
    from mdast_cli.distribution_systems.nexus import NexusRepository


def parse_args():
    parser = argparse.ArgumentParser(description='Start scan and get scan results.')
    parser.add_argument('--distribution_system', type=str, help='Select how to get apk file',
                        choices=['file', 'hockeyapp', 'appcenter', 'nexus'], required=True)

    # Arguments used for distribution_system = file
    parser.add_argument('--file_path', type=str, help='Path to local apk file for analyze. This argument required if '
                                                      'distribution system set to "file"')

    # Arguments used for distribution_system hockeyapp
    parser.add_argument('--hockey_token', type=str, help='Auth token for HockeyApp. This argument required if '
                                                         'distribution system set to "hockeyapp"')
    parser.add_argument('--hockey_bundle_id', type=str, help='Application bundle in HockeyApp. This argument or '
                                                             '"--hockey_public_id" required if distribution system '
                                                             'set to "hockeyapp"')
    parser.add_argument('--hockey_public_id', type=str, help='Application identifier in HockeyApp. This argument or '
                                                             '"--hockey_bundle_id" required if distribution system '
                                                             'set to "hockeyapp"')
    parser.add_argument('--hockey_version', type=str, help='Application version in HockeyApp. If not set - the latest '
                                                           'version will be downloaded. This argument required if '
                                                           'distribution system set to "hockeyapp"', default='latest')

    # Arguments used for distribution_system appcenter
    parser.add_argument('--appcenter_token', type=str, help='Auth token for AppCenter. This argument required if '
                                                            'distribution system set to "appcenter"')
    parser.add_argument('--appcenter_owner_name', type=str, help='Application owner name in AppCenter. This argument '
                                                                 'required if distribution system set to "appcenter"')
    parser.add_argument('--appcenter_app_name', type=str, help='Application name in AppCenter. This argument required '
                                                               'if distribution system set to "appcenter"')
    parser.add_argument('--appcenter_release_id', type=str, help='Release id in AppCenter. If not set - the latest '
                                                                 'release will be downloaded. This argument or '
                                                                 '"--ac_app_version" required if distribution system '
                                                                 'set to "appcenter"')
    parser.add_argument('--appcenter_app_version', type=str, help='Application version in AppCenter. This argument  or '
                                                                  '"--appcenter_release_id" required if distribution '
                                                                  'system set to "appcenter"')

    # Agruments for Nexus
    parser.add_argument('--nexus_url', type=str,
                        help='Http url for Nexus server where mobile application is located.'
                             ' This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_login', type=str,
                        help='Login for Nexus server where mobile application is located.'
                             ' This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_password', type=str,
                        help='Password for Nexus server where mobile application is located.'
                             'This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_repo_name', type=str,
                        help='Repository name in Nexus where mobile application is located. '
                             'This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_group_id', type=str,
                        help='Group_id for mobile application. '
                             'This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_artifact_id', type=str,
                        help='Artifact id for mobile application. '
                             'This argument required if distribution system set to "appcenter"')
    parser.add_argument('--nexus_version', type=str,
                        help='Version to download from Nexus. '
                             'This argument required if distribution system set to "appcenter"')

    # Main arguments
    parser.add_argument('--url', type=str, help='System url', required=True)
    parser.add_argument('--company_id', type=int, help='Company id for starting scan', required=True)
    parser.add_argument('--architecture_id', type=int, help='Architecture id to perform scan')
    parser.add_argument('--token', type=str, help='CI/CD Token for start scan and get results', required=True)
    parser.add_argument('--profile_id', type=int, help='Project id for scan', required=True)
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
    elif args.distribution_system == 'hockeyapp' and (
            args.hockey_token is None or
            (args.hockey_bundle_id is None or args.hockey_public_id is None)):
        parser.error('"--distribution_system hockeyapp" requires "--hockey_token" and "--hockey_app" arguments to be '
                     'set')
    elif args.distribution_system == 'appcenter' and (
            args.appcenter_token is None or args.appcenter_owner_name is None or args.appcenter_app_name is None or (
            args.appcenter_release_id is None and args.appcenter_app_version is None)):
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
    return args


def main():
    urllib3.disable_warnings()

    arguments = parse_args()

    url = arguments.url
    company_id = arguments.company_id
    architecture = arguments.architecture_id
    token = arguments.token
    profile_id = arguments.profile_id
    testcase_id = arguments.testcase_id
    json_summary_file_name = arguments.summary_report_json_file_name
    pdf_report_file_name = arguments.pdf_report_file_name
    distribution_system = arguments.distribution_system
    not_wait_scan_end = arguments.nowait

    url = url if url.endswith('/') else f'{url}/'
    url = url if url.endswith('rest/') else f'{url}rest'

    app_file = ''
    if distribution_system == 'file':
        app_file = arguments.file_path
        _, file_extension = os.path.splitext(arguments.file_path)
    elif distribution_system == 'hockeyapp':
        hockey_app = HockeyApp(arguments.hockey_token,
                               arguments.hockey_bundle_id,
                               arguments.hockey_public_id,
                               arguments.hockey_version)
        app_file = hockey_app.download_app()
        _, file_extension = os.path.splitext(app_file)
    elif distribution_system == 'appcenter':
        appcenter = AppCenter(arguments.appcenter_token,
                              arguments.appcenter_app_name,
                              arguments.appcenter_owner_name,
                              arguments.appcenter_app_version,
                              arguments.appcenter_release_id)
        app_file = appcenter.download_app()
        _, file_extension = os.path.splitext(app_file)
    elif distribution_system == 'nexus':
        nexus_repository = NexusRepository(arguments.nexus_url,
                                           arguments.nexus_login,
                                           arguments.nexus_password,
                                           arguments.nexus_repo_name,
                                           arguments.nexus_group_id,
                                           arguments.nexus_artifact_id,
                                           arguments.nexus_version)
        app_file = nexus_repository.download_app()
        _, file_extension = os.path.splitext(app_file)

    mdast = mDast(url, token, company_id)
    get_architectures_resp = mdast.get_architectures()
    if not get_architectures_resp.status_code == 200:
        Log.error(f'Error while getting architectures')
        sys.exit(1)

    if testcase_id is not None:
        get_testcase_resp = mdast.get_testcase(testcase_id)
        try:
            assert get_testcase_resp.status_code == 200, "wrong id"
        except AssertionError:
            print("Testcase with this id does not exist")
            sys.exit(1)
        architecture = get_testcase_resp.json()['architecture']['id']
    elif architecture is not None:
        pass
    else:
        if file_extension == ".apk":
            architecture = Architectures.ANDROID_11
        else:
            architecture = Architectures.iOS_14

    architectures = get_architectures_resp.json()
    architecture_type = next(arch for arch in architectures if arch.get('id', '') == architecture)
    try:
        if architecture_type is None:
            if file_extension == ".apk":
                architecture = Architectures.ANDROID_8
                architecture_type = next(arch for arch in architectures if arch.get('id', '') == architecture)
                assert architecture_type is not None
    except AssertionError:
        Log.error(f'Error while getting architectures, no suitable architecture for this app')
        sys.exit(1)

    Log.info(f'Start scan with test case Id: '
             f'{testcase_id}, profile Id: {profile_id} and file: {app_file}, architecture id is {architecture}')

    Log.info('Uploading application to server')
    upload_application_resp = mdast.upload_application(app_file, str(architecture_type['type']))
    if not upload_application_resp.status_code == 201:
        Log.error(f'Error while uploading application to server: {upload_application_resp.text}')
        sys.exit(1)

    application = upload_application_resp.json()
    Log.info(f"Application uploaded successfully. Application id: {application['id']}")

    Log.info(f"Create scan for application {application['id']}")

    # TODO Remove this after autoscan for ios will be available
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
        scan_type = 'auto'
    else:
        Log.error("Cannot create scan - unknown architecture")
        sys.exit(1)

    if not create_dast_resp.status_code == 201:
        Log.error(f'Error while creating scan: {create_dast_resp.text}')
        sys.exit(1)

    dast = create_dast_resp.json()
    if not 'id' in dast and dast.get('id', '') != '':
        Log.error(f'Something went wrong while creating scan: {dast}')
        sys.exit(1)

    if scan_type == 'auto':
        Log.info(f"Autoscan was created successfuly. Scan id: {dast['id']}")
    else:
        Log.info(f"Manual scan was created successfuly. Scan id: {dast['id']}")

    Log.info(f"Start scan with id {dast['id']}")
    start_dast_resp = mdast.start_scan(dast['id'])
    if not start_dast_resp.status_code == 200:
        Log.error(f"Error while starting scan with id {dast['id']}: {start_dast_resp.text}")
        sys.exit(1)

    if not_wait_scan_end:
        Log.info('Scan successfully started. Don`t wait for end, exit with zero code')
        sys.exit(0)

    Log.info(f"Scan started successfully.")
    Log.info(f"Check scan state with id {dast['id']}")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if not get_dast_info_resp.status_code == 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)

    dast = get_dast_info_resp.json()
    dast_status = dast['state']
    Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
    count = 0

    Log.info(f"Waiting until scan with id {dast['id']} started.")
    while dast_status in (DastState.CREATED, DastState.INITIALIZING, DastState.STARTING) and count < TRY_COUNT:
        Log.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if not get_dast_info_resp.status_code == 200:
            Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)

        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        Log.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
        time.sleep(SLEEP_TIMEOUT)

    if not dast['state'] in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING, DastState.SUCCESS):
        Log.error(f"Error with scan id {dast['id']}. Current scan status: {dast['state']},"
                  f" but expected to be {DastState.STARTED}, {DastState.ANALYZING}, {DastState.STOPPING} "
                  f"or {DastState.SUCCESS}")
        sys.exit(1)
    Log.info(f"Scan with {dast['id']} finished and now analyzing. Wait until analyzing stage is finished.")

    Log.info(f"Waiting until scan with id {dast['id']} finished.")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if not get_dast_info_resp.status_code == 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    dast = get_dast_info_resp.json()
    dast_status = dast['state']
    Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
    count = 0

    while dast_status in (DastState.STARTED, DastState.STOPPING, DastState.ANALYZING) and count < TRY_COUNT:
        if count == 0 and scan_type == 'manual':
            Log.info(f"This is manual scan, lets wait for {SLEEP_TIMEOUT} seconds and stop it.")
            time.sleep(SLEEP_TIMEOUT)
            stop_manual_dast_resp = mdast.stop_scan(dast['id'])
            if not stop_manual_dast_resp.status_code == 200:
                Log.error(f"Error while stopping scan with id {dast['id']}: {get_dast_info_resp.text}")
                sys.exit(1)

        Log.info(f"Try to get scan status for scan id {dast['id']}. Count number {count}")
        get_dast_info_resp = mdast.get_scan_info(dast['id'])
        if not get_dast_info_resp.status_code == 200:
            Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
            sys.exit(1)
        dast = get_dast_info_resp.json()
        dast_status = dast['state']
        Log.info(f"Current scan status: {DastStateDict.get(dast_status)}")
        count += 1
        Log.info(f"Wait {SLEEP_TIMEOUT} seconds and try again")
        time.sleep(SLEEP_TIMEOUT)

    Log.info(f"Check is scan with id {dast['id']} finished correctly.")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if not get_dast_info_resp.status_code == 200:
        Log.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(1)
    dast = get_dast_info_resp.json()

    if not dast['state'] == DastState.SUCCESS:
        Log.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)}, but in real it was {dast['state']}. "
            f"Exit with error status code.")
        sys.exit(1)

    if not dast['state'] == DastState.SUCCESS:
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

    Log.info('Job completed successfully')


if __name__ == '__main__':
    main()
