import argparse
import json
import os
import sys
import time

import urllib3

try:
    from distribution_systems.appstore import AppStore
    from distribution_systems.google_play import google_play_download
    from helpers.const import END_SCAN_TIMEOUT, SLEEP_TIMEOUT, TRY_COUNT, DastState, DastStateDict
    from helpers.logging import Log
except ImportError:
    from mdast_cli.distribution_systems.appstore import AppStore
    from mdast_cli.distribution_systems.google_play import google_play_download
    from mdast_cli.helpers.const import END_SCAN_TIMEOUT, SLEEP_TIMEOUT, TRY_COUNT, DastState, DastStateDict
    from mdast_cli.helpers.logging import Log


def parse_args():
    parser = argparse.ArgumentParser(description='Start download and get file.')
    parser.add_argument('--distribution_system', '-ds', type=str, help='Select how to download file: '
                                                                       'appstore/google_play',
                        choices=['appstore', 'google_play'], required=True)
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

    args = parser.parse_args()

    if args.distribution_system == 'appstore' and (
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
    app_file = ''
    if distribution_system == 'appstore':
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


if __name__ == '__main__':
    main()
