import argparse
import asyncio
import json
import logging
import os
import sys
import time
import warnings

import urllib3

# Suppress pkg_resources deprecation warning from google-auth
# This warning appears when google-auth is imported, even if not used
warnings.filterwarnings('ignore', message='.*pkg_resources is deprecated.*', category=UserWarning)

from mdast_cli.distribution_systems.appgallery import appgallery_download_app
from mdast_cli.distribution_systems.appstore import AppStore
from mdast_cli.distribution_systems.firebase import firebase_download_app
from mdast_cli.distribution_systems.google_play import GooglePlay
from mdast_cli.distribution_systems import google_play_apkeep as gp_apkeep
from mdast_cli.distribution_systems.nexus import NexusRepository
from mdast_cli.distribution_systems.nexus2 import Nexus2Repository
from mdast_cli.distribution_systems.rumarket import rumarket_download_app
from mdast_cli.distribution_systems.rustore import rustore_download_app
from mdast_cli.helpers.const import (ANDROID_EXTENSIONS, DEFAULT_ANDROID_ARCHITECTURE, DEFAULT_IOS_ARCHITECTURE,
                                     END_SCAN_TIMEOUT, LONG_TRY, SLEEP_TIMEOUT, TRY, DastState, DastStateDict)
from mdast_cli.helpers.exit_codes import ExitCode
from mdast_cli.helpers.helpers import check_app_md5
from mdast_cli_core.token import mDastToken as mDast
from mdast_cli.cr_report_generator import generate_cr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S', stream=sys.stdout)

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='MDast CLI - tool for downloading and scanning mobile applications.',
        epilog='''
Usage examples:
  # Download application from Google Play without scanning:
  mdast_cli -d --distribution_system google_play \\
    --google_play_package_name com.example.app \\
    --google_play_email user@example.com \\
    --google_play_aas_token YOUR_TOKEN

  # Start application scanning:
  mdast_cli --distribution_system file --file_path app.apk \\
    --url https://mdast.example.com --company_id 1 --token YOUR_TOKEN

For detailed information about specific distribution system see README.md
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main options
    main_group = parser.add_argument_group('Main Options', 'General parameters for utility operation')
    main_group.add_argument('--download_only', '-d', action='store_true',
                           help='Download application without starting scan. '
                                'When using this option, --url, --company_id, --token parameters are not required. '
                                'After successful download, file path is printed in format DOWNLOAD_PATH=/path/to/file')
    main_group.add_argument('--distribution_system', '-ds', type=str,
                           help='Application distribution system for downloading. '
                                'Available options: file, nexus, nexus2, firebase, appstore, google_play, '
                                'rustore, appgallery, rumarket. '
                                'System choice determines which additional parameters will be required.',
                           choices=['file', 'nexus', 'nexus2', 'firebase', 'appstore', 'google_play',
                                    'rustore', 'appgallery', 'rumarket'],
                           required=True)
    main_group.add_argument('--download_path', '-p', type=str,
                           help='Path to directory for saving downloaded applications. '
                                'Default: downloaded_apps. '
                                'Directory will be created automatically if it does not exist.',
                           default='downloaded_apps')

    # File distribution system
    file_group = parser.add_argument_group('Local File (file)', 
                                          'Using existing local application file')
    file_group.add_argument('--file_path', type=str,
                          help='Full path to local application file (APK for Android or IPA for iOS). '
                               'Required parameter when --distribution_system is set to "file". '
                               'Example: /path/to/app.apk or ./my_app.ipa')

    # Nexus distribution system
    nexus_group = parser.add_argument_group('Nexus Repository (nexus)',
                                           'Downloading applications from Nexus Repository Manager 3.x')
    nexus_group.add_argument('--nexus_url', type=str,
                            help='Nexus server URL (with http/https protocol). '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'Example: https://nexus.example.com or http://localhost:8081')
    nexus_group.add_argument('--nexus_login', type=str,
                            help='Username for Nexus authentication. '
                                 'Required parameter when --distribution_system is set to "nexus".')
    nexus_group.add_argument('--nexus_password', type=str,
                            help='Password for Nexus authentication. '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'It is recommended to use environment variables for security.')
    nexus_group.add_argument('--nexus_repo_name', type=str,
                            help='Repository name in Nexus where the application is located. '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'Example: releases, snapshots, maven-releases')
    nexus_group.add_argument('--nexus_group_id', type=str,
                            help='Application Group ID in Maven format (usually reverse domain). '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'Example: com.example, org.mycompany')
    nexus_group.add_argument('--nexus_artifact_id', type=str,
                            help='Application Artifact ID (artifact name). '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'Example: myapp, mobile-app')
    nexus_group.add_argument('--nexus_version', type=str,
                            help='Application version to download. '
                                 'Required parameter when --distribution_system is set to "nexus". '
                                 'Example: 1.0.0, 2.5.1, 1.0.0-SNAPSHOT')

    # Firebase distribution system
    firebase_group = parser.add_argument_group('Firebase App Distribution (firebase)',
                                              'Downloading applications from Firebase App Distribution')
    firebase_group.add_argument('--firebase_project_number', type=int,
                               help='Firebase project number (Project Number). '
                                    'Required parameter when --distribution_system is set to "firebase". '
                                    'Can be found in Firebase Console project settings. '
                                    'Example: 123456789012')
    firebase_group.add_argument('--firebase_app_id', type=str,
                               help='Application ID in Firebase in format: "1:PROJECT_NUMBER:PLATFORM:APP_ID". '
                                    'Required parameter when --distribution_system is set to "firebase". '
                                    'Examples: "1:123456789012:android:abc123def456", "1:123456789012:ios:xyz789"')
    firebase_group.add_argument('--firebase_account_json_path', type=str,
                               help='Path to JSON file with Firebase service account credentials. '
                                    'Required parameter when --distribution_system is set to "firebase". '
                                    'File can be downloaded from Firebase Console → Project Settings → Service Accounts. '
                                    'Example: /path/to/service-account.json or ./firebase-key.json')
    firebase_group.add_argument('--firebase_file_extension', type=str,
                               help='Application file extension for download. '
                                    'Required parameter when --distribution_system is set to "firebase". '
                                    'Available values: apk (Android) or ipa (iOS).',
                               choices=['ipa', 'apk'])
    firebase_group.add_argument('--firebase_file_name', type=str,
                               help='File name for saving application (without extension). '
                                    'Optional parameter. If not specified, version from Firebase is used. '
                                    'Example: my_app, production_build')

    # AppStore distribution system
    appstore_group = parser.add_argument_group('Apple App Store (appstore)',
                                              'Downloading applications from Apple App Store')
    appstore_group.add_argument('--appstore_app_id', type=str,
                               help='Application ID in App Store. Can be found in application page URL: '
                                    'https://apps.apple.com/app/id{APP_ID}. '
                                    'Either --appstore_app_id or --appstore_bundle_id must be specified. '
                                    'Example: 389801252 (Instagram), 310633997 (WhatsApp)')
    appstore_group.add_argument('--appstore_bundle_id', type=str,
                               help='Application Bundle ID (package identifier). '
                                    'Either --appstore_app_id or --appstore_bundle_id must be specified. '
                                    'Example: com.instagram.ios, com.whatsapp.WhatsApp')
    appstore_group.add_argument('--appstore_apple_id', type=str,
                               help='Apple ID email address for iTunes/App Store login. '
                                    'Required parameter when --distribution_system is set to "appstore". '
                                    'Example: user@example.com')
    appstore_group.add_argument('--appstore_password', type=str,
                               help='Apple ID password. '
                                    'Required parameter when --distribution_system is set to "appstore". '
                                    'It is recommended to use environment variables for security.')
    appstore_group.add_argument('--appstore_2FA', type=str,
                               help='Two-factor authentication code (6 digits). '
                                    'Required parameter when --distribution_system is set to "appstore". '
                                    'Code is sent to trusted Apple devices. '
                                    'Example: 123456')
    appstore_group.add_argument('--appstore_file_name', type=str,
                               help='File name for saving application (without .ipa extension). '
                                    'Optional parameter. If not specified, application name and version are used. '
                                    'Example: my_app, instagram_latest')
    appstore_group.add_argument('--appstore_password2FA', type=str,
                               help='[DEPRECATED] Password and 2FA code in one parameter (format: password2FA_code). '
                                    'Use --appstore_password and --appstore_2FA instead of this parameter. '
                                    'Will be removed in future versions.',
                               metavar='DEPRECATED')

    # Google Play distribution system
    google_play_group = parser.add_argument_group('Google Play (google_play)',
                                                  'Downloading applications from Google Play Store using apkeep')
    google_play_group.add_argument('--google_play_package_name', type=str,
                                  help='Application package name from Google Play. '
                                       'Required parameter when --distribution_system is set to "google_play". '
                                       'Can be found in application page URL: '
                                       'https://play.google.com/store/apps/details?id={PACKAGE_NAME}. '
                                       'Examples: com.instagram.android, com.whatsapp, org.telegram.messenger')
    google_play_group.add_argument('--google_play_email', type=str,
                                  help='Google account email address. '
                                       'Required parameter when --distribution_system is set to "google_play". '
                                       'Used together with --google_play_aas_token or --google_play_oauth2_token. '
                                       'Example: user@gmail.com')
    google_play_group.add_argument('--google_play_aas_token', type=str,
                                  help='AAS token for Google Play (obtained via apkeep). '
                                       'Used for subsequent downloads after first token acquisition. '
                                       'Requires --google_play_email. '
                                       'Format: aas_et/... (long string). '
                                       'For first run use --google_play_oauth2_token.')
    google_play_group.add_argument('--google_play_oauth2_token', type=str,
                                  help='OAuth2 token to obtain AAS token via apkeep. '
                                       'Used on first run. After obtaining AAS token, you can use '
                                       '--google_play_aas_token for subsequent downloads. '
                                       'Requires --google_play_email. '
                                       'Format: ya29.a0AVvZVs... (OAuth2 access token)')
    google_play_group.add_argument('--google_play_file_name', type=str,
                                  help='File name for saving application (without extension). '
                                       'Optional parameter. If not specified, package name is used. '
                                       'Example: instagram_latest, whatsapp_production')
    google_play_group.add_argument('--google_play_proxy', type=str,
                                  help='Proxy settings for connecting to Google Play. '
                                       'Optional parameter. '
                                       'Format: socks5://user:pass@host:port or http://user:pass@host:port. '
                                       'Example: socks5://proxy.example.com:1080')

    # RuStore distribution system
    rustore_group = parser.add_argument_group('RuStore (rustore)',
                                             'Downloading applications from Russian RuStore marketplace')
    rustore_group.add_argument('--rustore_package_name', type=str,
                              help='Application package name from RuStore. '
                                   'Required parameter when --distribution_system is set to "rustore". '
                                   'Can be found in application page URL. '
                                   'Examples: com.vkontakte.android, com.yandex.browser')

    # RuMarket distribution system
    rumarket_group = parser.add_argument_group('RuMarket (rumarket)',
                                              'Downloading applications from Russian RuMarket marketplace')
    rumarket_group.add_argument('--rumarket_package_name', type=str,
                                help='Application package name from RuMarket. '
                                     'Required parameter when --distribution_system is set to "rumarket". '
                                     'Example: com.example.app')

    # AppGallery distribution system
    appgallery_group = parser.add_argument_group('Huawei AppGallery (appgallery)',
                                                'Downloading applications from Huawei AppGallery')
    appgallery_group.add_argument('--appgallery_app_id', type=str,
                                  help='Application ID in AppGallery. '
                                       'Required parameter when --distribution_system is set to "appgallery". '
                                       'Can be found in application page URL: '
                                       'https://appgallery.huawei.com/app/{APP_ID}. '
                                       'Format: C + digits, e.g.: C101184875, C100000001')
    appgallery_group.add_argument('--appgallery_file_name', type=str,
                                 help='File name for saving application (without .apk extension). '
                                      'Optional parameter. If not specified, package name and version are used. '
                                      'Example: huawei_app, instagram_huawei')

    # Nexus2 distribution system
    nexus2_group = parser.add_argument_group('Nexus Repository 2.x (nexus2)',
                                            'Downloading applications from Nexus Repository Manager 2.x')
    nexus2_group.add_argument('--nexus2_url', type=str,
                             help='Nexus 2.x server URL (with http/https protocol and /nexus/ path). '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Example: http://nexus.example.com:8081/nexus/ or http://localhost:8081/nexus/')
    nexus2_group.add_argument('--nexus2_login', type=str,
                             help='Username for Nexus 2.x authentication. '
                                  'Required parameter when --distribution_system is set to "nexus2".')
    nexus2_group.add_argument('--nexus2_password', type=str,
                             help='Password for Nexus 2.x authentication. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'It is recommended to use environment variables for security.')
    nexus2_group.add_argument('--nexus2_repo_name', type=str,
                             help='Repository name in Nexus 2.x where the application is located. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Example: releases, snapshots')
    nexus2_group.add_argument('--nexus2_group_id', type=str,
                             help='Application Group ID in Maven format. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Example: com.example, org.mycompany')
    nexus2_group.add_argument('--nexus2_artifact_id', type=str,
                             help='Application Artifact ID. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Example: myapp, android-app')
    nexus2_group.add_argument('--nexus2_version', type=str,
                             help='Application version to download. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Example: 1.0.0, 2.5.1, 1.0.0-SNAPSHOT')
    nexus2_group.add_argument('--nexus2_extension', type=str,
                             help='Application file extension. '
                                  'Required parameter when --distribution_system is set to "nexus2". '
                                  'Usually: apk (Android) or ipa (iOS). '
                                  'Example: apk, ipa, zip')
    nexus2_group.add_argument('--nexus2_file_name', type=str,
                             help='File name for saving application (without extension). '
                                  'Optional parameter. If not specified, generated automatically. '
                                  'Example: my_app, production_build')

    # Scanning arguments
    scan_group = parser.add_argument_group('Scanning Parameters',
                                          'Parameters for starting and managing application scanning')
    scan_group.add_argument('--url', type=str,
                           help='MDast server URL for submitting application for scanning. '
                                'Required parameter when starting scan (without --download_only). '
                                'Example: https://mdast.example.com',
                           required=(not '-d'))
    scan_group.add_argument('--company_id', type=int,
                           help='Company ID in MDast system. '
                                'Required parameter when starting scan (without --download_only). '
                                'Can be found in company settings in MDast web interface.',
                           required=(not '-d'))
    scan_group.add_argument('--token', type=str,
                           help='CI/CD token for authentication and starting scan. '
                                'Required parameter when starting scan (without --download_only). '
                                'Token can be obtained in profile settings in MDast web interface. '
                                'It is recommended to use environment variables for security.',
                           required=(not '-d'))
    scan_group.add_argument('--architecture_id', type=int,
                           help='Architecture ID for performing scan. '
                                'Optional parameter. If not specified, default architecture is used. '
                                'List of available architectures can be obtained via MDast API.')
    scan_group.add_argument('--profile_id', type=int, default=None,
                           help='Profile ID for scanning. '
                                'Optional parameter. If not specified, profile will be created automatically.')
    scan_group.add_argument('--project_id', type=int, default=None,
                           help='Project ID for scanning. '
                                'Optional parameter. Used only when auto-creating profile '
                                'to place new profile in existing project.')
    scan_group.add_argument('--testcase_id', type=int,
                           help='Test case ID for automatic scanning. '
                                'Optional parameter. If not specified, manual scanning is performed.')
    scan_group.add_argument('--appium_script_path', type=str,
                           help='Path to Appium script for automatic scanning using Stingray Appium. '
                                'Optional parameter. Used for automated testing.')
    scan_group.add_argument('--summary_report_json_file_name', type=str,
                           help='File name for saving JSON report with scan results in structured format. '
                                'Optional parameter. If specified, report will be saved to specified file.')
    scan_group.add_argument('--pdf_report_file_name', type=str,
                           help='File name for saving PDF report with scan results. '
                                'Optional parameter. If specified, PDF report will be saved to specified file.')
    scan_group.add_argument('--nowait', '-nw', action='store_true',
                           help='Do not wait for scan completion. '
                                'If set, utility will start scan and exit immediately. '
                                'If not set, utility will wait for scan completion and output results.')
    scan_group.add_argument('--long_wait', action='store_true',
                           help='Increase time limit for waiting scan completion to 1 week. '
                                'By default, standard timeout is used.')

    # CR Report arguments
    cr_report_group = parser.add_argument_group('CR Report Parameters',
                                                'Parameters for generating Compliance Report (CR)')
    cr_report_group.add_argument('--cr_report', action='store_true',
                                help='Enable CR report generation after scan completion. '
                                     'CR report contains information about application compliance with security requirements.')
    cr_report_group.add_argument('--stingray_login', type=str,
                               help='Login for accessing Stingray system for CR report generation. '
                                    'Required parameter when using --cr_report.')
    cr_report_group.add_argument('--stingray_password', type=str,
                                help='Password for accessing Stingray system for CR report generation. '
                                     'Required parameter when using --cr_report. '
                                     'It is recommended to use environment variables for security.')
    cr_report_group.add_argument('--organization_name', type=str,
                                help='Organization name for CR report. '
                                     'Default: ООО Стингрей Технолоджиз',
                                default='ООО Стингрей Технолоджиз')
    cr_report_group.add_argument('--engineer_name', type=str,
                                help='Engineer name to be specified in CR report. '
                                     'Optional parameter.')
    cr_report_group.add_argument('--controller_name', type=str,
                                help='Controller name to be specified in CR report. '
                                     'Optional parameter.')
    cr_report_group.add_argument('--use_ldap', type=str,
                                help='Use LDAP for authentication when generating CR report. '
                                     'Default: False. '
                                     'Optional parameter.',
                                default=False)
    cr_report_group.add_argument('--authority_server_id', type=str,
                                help='Authority server ID for CR report. '
                                     'Optional parameter. Used when working with LDAP.',
                                default=None)
    cr_report_group.add_argument('--cr_report_path', type=str,
                                help='Path for saving CR report. '
                                     'Default: stingray-CR-report.html. '
                                     'Optional parameter.',
                                default='stingray-CR-report.html')





    args = parser.parse_args()

    if args.distribution_system == 'file' and args.file_path is None:
        parser.error('"--distribution_system file" requires "--file_path" argument to be set')
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

    elif args.distribution_system == 'google_play':
        if args.google_play_package_name is None:
            parser.error('"--distribution_system google_play" requires "--google_play_package_name" to be set')
        # 1) email + aas_token
        # 2) email + oauth2_token (we will fetch aas_token automatically)
        email_aas_ok = (args.google_play_email is not None and args.google_play_aas_token is not None)
        email_oauth2_ok = (args.google_play_email is not None and args.google_play_oauth2_token is not None)
        if not (email_aas_ok or email_oauth2_ok):
            parser.error(
                '"--distribution_system google_play" requires one of: '
                '(1) "--google_play_email" + "--google_play_aas_token", '
                '(2) "--google_play_email" + "--google_play_oauth2_token".'
            )

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
        cr_report = arguments.cr_report
        stingray_login = arguments.stingray_login
        stingray_password = arguments.stingray_password
        organization_name = arguments.organization_name
        engineer_name = arguments.engineer_name
        controller_name = arguments.controller_name
        use_ldap = arguments.use_ldap
        authority_server_id = arguments.authority_server_id
        cr_report_path = arguments.cr_report_path


        url = url if url.endswith('/') else f'{url}/'
        url = url if url.endswith('rest/') else f'{url}rest'

    app_file = ''
    appstore_app_md5 = None

    try:
        if distribution_system == 'file':
            app_file = arguments.file_path

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
            # Resolve AAS token from OAuth2 if provided and AAS not given
            resolved_aas_token = arguments.google_play_aas_token
            if (not resolved_aas_token) and arguments.google_play_oauth2_token:
                try:
                    resolved_aas_token = asyncio.run(
                        gp_apkeep.fetch_aas_token(
                            email=arguments.google_play_email or '',
                            oauth2_token=arguments.google_play_oauth2_token,
                            timeout_sec=gp_apkeep.DEFAULT_TIMEOUT_SEC
                        )
                    )
                except Exception as ex:
                    logger.error(f'Failed to obtain AAS token via OAuth2: {ex}')
                    sys.exit(ExitCode.AUTH_ERROR)

            google_play = GooglePlay(arguments.google_play_email,
                                     resolved_aas_token)
            google_play.login()

            app_file = google_play.download_app(download_path,
                                                arguments.google_play_package_name,
                                                arguments.google_play_file_name, proxy=arguments.google_play_proxy)

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
        sys.exit(ExitCode.DOWNLOAD_FAILED)

    if arguments.download_only is True:
        logger.info('Your application was downloaded!')
        # Emit a single-line machine-friendly output for CI parsers
        print(f'DOWNLOAD_PATH={app_file}')
        sys.exit(ExitCode.SUCCESS)

    mdast = mDast(url, token, company_id)
    get_architectures_resp = mdast.get_architectures()

    if get_architectures_resp.status_code != 200:
        logger.error(f'Error while getting architectures. Server response: {get_architectures_resp.text}')
        sys.exit(ExitCode.NETWORK_ERROR)

    architectures = get_architectures_resp.json()

    _, file_extension = os.path.splitext(app_file)

    if architecture is None:
        if file_extension in ANDROID_EXTENSIONS:
            architecture = next((arch['id'] for arch in architectures if arch.get('name', '') == DEFAULT_ANDROID_ARCHITECTURE), None)
        if file_extension == '.ipa':
            architecture = next((arch['id'] for arch in architectures if arch.get('name', '') == DEFAULT_IOS_ARCHITECTURE), None)
        if architecture is None:
            logger.error(f"Cannot create scan - no suitable architecture for this app, try to set it manually with --architecture_id")
            sys.exit(ExitCode.INVALID_ARGS)
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
        sys.exit(ExitCode.SCAN_FAILED)

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
            sys.exit(ExitCode.SCAN_FAILED)
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
        sys.exit(ExitCode.SCAN_FAILED)

    dast_info = create_dast_resp.json()
    logger.info(f"Project and profile was created/found successfully."
                f" Project id: {dast_info['project']['id']}, profile id: {dast_info['profile']['id']}")

    dast = create_dast_resp.json()
    if 'id' not in dast or dast.get('id', '') == '':
        logger.error(f'Something went wrong while creating scan: {dast}')
        sys.exit(ExitCode.SCAN_FAILED)

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
        sys.exit(ExitCode.SCAN_FAILED)

    if not_wait_scan_end:
        logger.info('Scan successfully started. Don`t wait for end, exit with zero code')
        sys.exit(ExitCode.SUCCESS)

    logger.info("Scan started successfully.")
    logger.info(f"Checking scan state with id {dast['id']}")
    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(ExitCode.NETWORK_ERROR)

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
        sys.exit(ExitCode.SCAN_FAILED)
    logger.info(f"Scan {dast['id']} is started now. Let's wait until the scan is finished")

    get_dast_info_resp = mdast.get_scan_info(dast['id'])
    if get_dast_info_resp.status_code != 200:
        logger.error(f"Error while getting scan info with id {dast['id']}: {get_dast_info_resp.text}")
        sys.exit(ExitCode.NETWORK_ERROR)
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
                    sys.exit(ExitCode.SCAN_FAILED)
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
        sys.exit(ExitCode.NETWORK_ERROR)
    dast = get_dast_info_resp.json()

    if dast['state'] != DastState.SUCCESS:
        logger.error(
            f"Expected state {DastStateDict.get(DastState.SUCCESS)}, but in real it was {dast['state']}. "
            f"Exit with error status code.")
        sys.exit(ExitCode.SCAN_FAILED)

    if pdf_report_file_name:
        logger.info(f"Create and download pdf report for scan with id {dast['id']} to file {pdf_report_file_name}.")
        pdf_report = mdast.download_report(dast['id'])
        if pdf_report.status_code != 200:
            logger.error(f"PDF report creating failed with error {pdf_report.text}. Exit...")
            sys.exit(ExitCode.SCAN_FAILED)

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
            sys.exit(ExitCode.SCAN_FAILED)

        logger.info(f"Saving summary json results to file {json_summary_file_name}.")
        mdast_json_file = json_summary_file_name if json_summary_file_name.endswith(
            '.json') else f'{json_summary_file_name}.json'
        with open(mdast_json_file, 'w') as fp:
            json.dump(json_summary_report.json(), fp, indent=4, ensure_ascii=False)

        logger.info(f"JSON report for scan {dast['id']} successfully created and available at path: {mdast_json_file}.")

    if cr_report:
        generate_cr(f"{url}", stingray_login, stingray_password, dast['id'], organization_name, engineer_name,
                    controller_name, cr_report_path, use_ldap, authority_server_id)

    logger.info('Job completed successfully!')


if __name__ == '__main__':
    main()
