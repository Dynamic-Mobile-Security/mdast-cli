<h1>Mobile DAST CI/CD</h1>

**Python script for automating security analysis of mobile applications.**

[![Docker Hub](https://img.shields.io/docker/v/mobilesecurity/mdast_cli?label=docker%20hub)](https://hub.docker.com/repository/docker/mobilesecurity/mdast_cli)
[![PyPi](https://img.shields.io/pypi/v/mdast_cli?color=3)](https://pypi.org/project/mdast-cli/)
![GitHub issues](https://img.shields.io/github/issues-raw/Dynamic-Mobile-Security/mdast-cli)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/Dynamic-Mobile-Security/mdast-cli)


This script is designed to integrate mobile applications' security analysis in the continuous development process (CI / CD).  
You can also only download applications from supported integrations with distribution systems without scanning.

During the execution of the script, the application is sent for the dynamic analysis. The output is a json/pdf file with detailed results. You can use the local file or download the application from one of the distribution systems. You should have write permissions to download the application.


* [Install options](#install-options)
    * [DockerHub](#dockerhub)
    * [PyPi](#from-pypi)
    * [Source](#source)
* [Launch options](#launch-options)
* [Launch parameters](#launch-parameters)
   * [Download only](#download-only)
   * [Scan parameters](#scan-parameters)
* [Distribution systems](#distribution-systems)
  * [Local file](#local-file-launch)
  * [Google play](#google-play)
  * [AppStore](#appstore)
  * [Firebase](#firebase)
  * [AppCenter](#appcenter)
  * [Nexus](#nexus)
* [Scan types](#scan-types)


## Install options

### DockerHub
You can run this script using [docker image](https://hub.docker.com/r/mobilesecurity/mdast_cli):

`docker pull mobilesecurity/mdast_cli:latest`

### From PyPi

It is possible to install a package using pip:

`pip install mdast_cli`

With this method, it is possible to start scanning without specifying the `python` interpreter using the` mdast_cli` command, for example:

`mdast_cli -h`

All examples below will use exactly this approach.

### Source

It also supports launching by loading source files and launching the main script directly:

`python3 mdast_cli/mdast_scan.py -h`

With this method of launching, you must additionally install the packages specified in `requirements.txt`


## Launch options

Currently, several distribution systems are supported:
 * Local file
 * Applications from [Google Play](https://play.google.com/store/apps)
 * Applications from [Appstore](https://www.apple.com/app-store/)
 * Applications from [Firebase](https://firebase.google.com/)
 * Applications from [AppCenter](https://appcenter.ms)
 * Applications from [Nexus Repository 3.x](https://help.sonatype.com/repomanager3) from maven repo.

## Launch parameters

#### Download only

If you just want to download the application without scanning, specify `--download_only` or `-d`  
After that you will need to specify the distribution system and mandatory parameters for specified system

* `distribution_system` - distribution method for the application   
_possible values_ `file`/`google_play`/`appstore`/`firebase`/`appcenter`/`nexus`   
For detailed information refer to the respective sections below.

If you want to integrate security analysis of downloaded application in the CI/CD you should specify these parameters.  

#### Scan parameters

The launch options depend on the location of the apk file sent for analysis. Also, there are required parameters that must be specified for launch:
 * `url` - network address for system (the path to the root without the final /)
 * `profile_id` - ID of the profile to be analyzed
 * `testcase_id` - ID of the test case to be executed. This is an optional parameter, if not set - manual scan with 20 seconds delay until finish will be executed;
 * `token` - CI/CD access token (refer to our documentation for ways to retrieve the token)
 * `company_id` - identifier of the company within which the scan will be performed
 * `architecture_id` - identifier of the operating system architecture on which the scan will be performed
 * `nowait` - an optional parameter specifying whether to wait for the scan to complete. If this flag is set, the script will not wait for the scan to complete but will exit immediately after starting. If the flag is not selected, the script will wait for the completion of the analysis process and generate a report.
 * `summary_report_json_file_name` - an optional parameter defining the name of the json file into which the scanning information in json format is uploaded. If the parameter is absent, the information will not be saved.
 * `pdf_report_file_name` - an optional parameter that specifies the name of the pdf file into which information on scanning in pdf format is uploaded. If the parameter is absent, the report will not be saved.

## Distribution systems

### Local file launch

#### Parameters

This type of launch implies that the application file is located locally.
To select this method at startup, you must specify the parameter `distribution_system file`.  
In this case, the required parameter must specify the path to the file: `file_path`

#### Launch example

__Docker launch__  
After pulling run docker using command like this (all parameters are applied due to distribution_system choice):

```
docker run -it -v {path_to_folder_with_application}:/mdast/files -v {path_to_report_folder}:/mdast/report mobilesecurity/mdast_cli:latest --profile_id 1 --architecture_id 5 --testcase_id 4 --distribution_system file --file_path /mdast/files/{application_file_name} --url "https://saas.mobile.appsec.world" --company_id 1 --token eyJ0eXA4OiJKA1Q**********U4I1NiJ1 --summary_report_json_file_name /mdast/report/json-report.json --pdf_report_file_name /mdast/report/pdf-report.pdf
```

Where:
 * `{path_to_folder_with_application}` - absolute path to the folder where build application locating
 * `{path_to_report_folder}` - absolute path to the folder where reports will be generated
 * `{application_file_name}` - full name of the built apk inside the `{path_to_folder_with_application}` folder


__Standard launch method__
```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4Oi**************I1NiJ1.eyJzdaJqZWNcX**************8OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```

As a result, automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched.

__Start without waiting for the scan to complete__
```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4Oi**************I1NiJ1.eyJzdaJqZWNcX**************8OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```
As a result, automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched and the script will finish immediately after starting the scan and will not wait for the end and generate a report.

__Generating a Summary report in JSON format__
```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4Oi**************I1NiJ1.eyJzdaJqZWNcX**************8OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2" --summary_report_json_file_name json-scan-report.json
```
As a result, automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched, and upon completion of scanning, a JSON report with the total number of defects and brief statistics will be saved.

### Google play

> :bangbang: :bangbang: :bangbang: *Updated May 2022*:   
> Seems like in last update Google disabled app passwords for play store access, so currently login with email + password is not working. If you already have gsfid + token just use them for now.  
Contact your suppport team if you need help, we will share with you working credentials from service account.

To download application from Google Play Store you need **temporary account with 2fa authentication disabled**.  

You should specify the package name of the application you want to download, you can get it directly from the Google Play app page or any other way.


Also, you need to select the `distribution_system google_play`.  

During the initial launch of the script you should specify the mandatory parameters: email + password, after that the application will not be downloaded if you don't specify optional parameter `google_play_download_with_creds` and the scan will not run, but you will **receive gsfid and token** for google authentication, which you should use later on for the successful Google Play application scan.  

#### Parameters
 * `google_play_package_name` - package name of application you want to download
 * `google_play_email` - email of your Google account for first login only
 * `google_play_password` - password of your Google account for login only

You can download app while logging in by email and password with an optional parameter:

 * `google_play_download_with_creds` - app will be downloaded during initial login  


At the initial run of the script you will get the **gsfId** and **auth token** in the script logs, you should copy and save them. They are required for stable and successful execution of the script afterwards.

![gsfid_token_logs](https://user-images.githubusercontent.com/46852358/162791052-fbce7121-1430-49ca-a9b9-68997391abd6.png)  

Using these parameters you will have all parameters for successful downloading applications from Google Play Store:

 * `google_play_package_name` - package name of application you want to download
 * `google_play_gsfid` - The Google Services Framework Identifier (GSF ID)
 * `google_play_auth_token` - Google auth token for access to Google Play API

You can also specify downloaded app file name with an optional parameter

 * `google_play_file_name` - file name for app to be saved with  

You should use either email + pass ("--google_play_email" + "--google_play_password") or gsfid + token ("--google_play_gsfid" + "google_play_auth_token") arguments for mdast_cli script. For the continuous process you need only gsfid and token.

#### Launch example

To start the initial login for Google Play, you need to run the following command:
```
 python mdast_cli/mdast_scan.py -d --distribution_system google_play --google_play_package_name com.instagram.android --google_play_email download*******ly@gmail.com --google_play_password Paaswoord
```
To start the manual scan analysis of the application from Google Play, you need to run the following command:

```
 python mdast_cli/mdast_scan.py --profile_id 1337 --architecture_id 1 --distribution_system google_play --url "https://saas.mobile.appsec.world" --company_id 1 --token 5d5f6c98*********487a68ee20d4562d9f --google_play_package_name com.instagram.android --google_play_gsfid 432******************43 --google_play_auth_token JAgw_2h*************************************8KRaYQ. --google_play_file_name best_apk_d0wnl04d3r
```

As a result in the `downloaded_apps` repository will be application with name `best_apk_d0wnl04d3r.apk` and manual scan will be started.

### AppStore
To download application from AppStore you need to know application_id and have **iTunes account** and credentials for it: email and password with 2FA code.  


You need to select the `--distribution_system appstore` and specify mandatory parameters.


To successfully sign in to iTunes, you will need to **obtain and save** the 2fa code for later use.  
When you run the script for the first time, use your email and password, you will get a login error in the console and at this point a two-factor authentication code will come to your device  


<img src="https://user-images.githubusercontent.com/46852358/153638449-6488cf6d-214f-44cb-8265-fe8b79b2614f.png" alt="drawing" width="300"/>  



For the subsequent work of the script without repeating the step with the manual receipt of 2fa code you need to remember the received code, the session with it will be active for 6 months. After that, try to repeat the login with  password and 2FA, formatting it like `password2FA`. You do not need to get new 2fa codes later, this parameter will work for 6 months.   

For example, password is `P@ssword` and 2FA is `742877`, so your parameter `--appstore_password2FA P@ssword742877`.

To get the app_id, go to the app page in the AppStore in your browser, you can extract the required parameter from the url:
![app_id_example](https://user-images.githubusercontent.com/46852358/153639003-f121273a-41ac-415d-aad7-6b2789f77cee.png)  

`appstore_app_id 398129933` in this example.  

#### Parameters

 You need to select the `distribution_system appstore` and specify the following mandatory parameters:
* `appstore_bundle_id` or `appstore_app_id`
  * `appstore_bundle_id` - bundle id of application
  * `appstore_app_id` - Application id from AppStore, you can get it on app page from url,   
format: apps.apple.com/app/id{appstore_app_id}
* `appstore_apple_id` - Your email for iTunes login.
* `appstore_password2FA` - Your password and 2FA code for iTunes login, format: password2FA_code 

You can specify downloaded app file name with an optional parameter

 * `appstore_file_name` - file name for app to be saved with

#### Launch example

To start the manual scan analysis of the application from AppStore, you need to run the following command:
```
 python mdast_cli/mdast_scan.py --architecture_id 3 --profile_id 1246 --distribution_system appstore --appstore_app_id 564177498 --appstore_apple_id ubet******@icloud.com --appstore_password2FA pass*******31******454  --url "https://saas.mobile.appsec.world" --company_id 2 --token 5d5f6****************2d9f --appstore_file_name my_b3st_4pp
```
As a result in the `downloaded_apps` repository will be application with name `my_b3st_4pp.ipa` and manual scan will be started.

#### Details

If you lost the 2fa code and the login has already been made, the session will be active for a few time without using 2fa, only apple_id + password. You also will not be able to end your session via this script, so for the script to work correctly you need to login again after session expires and save the two-factor authentication code in your notes.  

If there is an error associated with the wrong Apple ID when you start scanning:

![wrong_apple_id](https://user-images.githubusercontent.com/46852358/158440208-45868069-d772-4476-a1bf-6508c2bac1eb.jpg)   

or error in logs:

"Logging in to the App Store. To open app, log in with the Apple ID with which you made the purchase."

Then contact the support team to agree on an Apple ID, which will be used for AppStore integration, you will be offered a solution to this problem.

While creating AppStore integration [ipatool](https://github.com/majd/ipatool) helped a lot, huge thanks for everyone who contributed to this nice open-source tool.

### Firebase
To download the application from firebase platform you need to know some cookies for Google SSO authentication and project_id, app_id, app_code, api_key and file_extension parameters from firebase project.  
You need to select the `--distribution_system firebase` and specify mandatory parameters.  

First, you should log in via Google SSO to [Firebase](https://console.firebase.google.com/u/0/) and get necessary cookies from your Chrome session local storage(F12 -> Application -> Cookies)  
And copy SID, SSID, APISID, SAPISID, HSID to your launch command. The lifetime of them are 2 years, so you don't have to do it often :)  

Screenshot of cookie storage:
![cookie_storage](https://user-images.githubusercontent.com/46852358/149788352-d453dd78-547f-4989-8132-b94a6f020a81.png)

#### Parameters

 * `firebase_SID_cookie` - SID
 * `firebase_HSID_cookie` - HSID
 * `firebase_SSID_cookie` - SSID
 * `firebase_APISID_cookie` - APISID
 * `firebase_SAPISID_cookie` - SAPISID

Now you need project_id, app_id, app_code, api_key to complete parameters for the scan. To get them go to:

App Project home page, url looks like this `https://console.firebase.google.com/u/0/project/{project_name}/overview` ->
![app_project](https://user-images.githubusercontent.com/46852358/149789837-2787cb52-355d-4ef0-9440-89053764db78.png)

to `Release & Monitor -> App Distribution` ->
![distr_page](https://user-images.githubusercontent.com/46852358/149791304-2658f1be-9ee0-422e-94ce-59f1ba1858df.png)  

Open network console(F12 -> Network -> Clear) and click `Download`

You will get this request in DevTools:
![download_req](https://user-images.githubusercontent.com/46852358/149792212-512d33ab-2323-45b6-a25c-6a8d817cde1f.png)  

And url will be like:  

`https://firebaseappdistribution-pa.clients6.google.com/v1/projects/{project_id}/apps/{app_id}/releases/{app_code}:getLatestBinary?alt=json&key={api_key}`  

So, you just extract missing parameters from this request and your launch command for CI/CD mobile applications' security analysis is ready!
Request url will match this pattern, you should extract 4 parameters from url.
`/v1/projects/{project_id}/apps/{app_id}/releases/{app_code}:getLatestBinary?alt=json&key={api_key}`  

 * `firebase_project_id` - project id of your Firebase project
 * `firebase_app_id` - application id
 * `firebase_app_code` - application code
 * `firebase_api_key` - your api key
 * `firebase_app_extension` - your app extension, it can be `apk` for android and `ipa` for iOS

You can specify the downloaded app file name with an optional parameter

 * `firebase_file_name` - file name for app to be saved with

#### Launch example

To start the manual scan analysis of the application, that was downloaded from Firebase, you need to run the following command:
```
python mdast_cli/mdast_scan.py --profile_id 468 --architecture_id 2 --distribution_system firebase --firebase_project_id 2834204**** --firebase_app_id 1:283***3642:android:8b0a0***56ac40c1a43 --firebase_app_code 2b***sltr0 --firebase_api_key AIzaSyDov*****qKdbj-geRWyzMTrg --firebase_SID_cookie FgiA*****ZiQakQ-_C-5ZaEHvbDMFGkrgriAByQ9P9fv7LfRrYJ5suXgrCwIQBoOjA. --firebase_HSID_cookie AsiL****OjPI --firebase_SSID_cookie A****dwcZk1Z-1pE --firebase_APISID_cookie Z-FmS1aPB****djK/AjmG0h2Hc-GG9g2Ac --firebase_SAPISID_cookie XYR2tnf****0zOt/AEvVZ8JVEuCnE6pxm --url "https://saas.mobile.appsec.world" --company_id 1 --token 2fac9652a2fbe4****9f44af59c3381772f --firebase_file_name your_app_file_name  --firebase_file_extension apk
```
As a result in the `downloaded_apps` repository will be application with name `your_app_file_name.apk` and manual scan will be started.

### AppCenter

#### Parameters

To download the application from AppCenter distribution system you need to select the `distribution_system appcenter` parameter. Also, you need to specify the following mandatory parameters:
 * `appcenter_token` - API access token. Look in official documentation to [learn how to retrieve it]((https://docs.microsoft.com/en-us/appcenter/api-docs/)).
 * `appcenter_owner_name` - owner of the application. Look in official documentation to learn how to retrieve the [owner name](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name).
 * `appcenter_app_name` - the name of the application in the AppCenter system. Look in official documentation to [learn how to retrieve it](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name)
 * `appcenter_release_id` or `appcenter_app_version`
    * `appcenter_release_id` - ID of the specific release of the application to be downloaded from AppCenter. There is a possibility to select the "latest" value - the [latest available version](https://openapi.appcenter.ms/#/distribute/releases_getLatestByUser) of the application will be downloaded.
    * `appcenter_app_version` - this parameter finds and downloads the specific version of the application by its version ID (shown in Android Manifest) (the "version" field in the [AppCenter Documentation](https://openapi.appcenter.ms/#/distribute/releases_list))

#### Launch examples

__AppCenter with the release ID__  

To start scanning an application using its name, the name of the owner and the release ID, the following command should be entered:

```
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name test_org_or_user --appcenter_app_name demo_app --appcenter_release_id 710 --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, the `demo_app` application with release `id 710` will be found among applications of the specified owner (user or organization `test_org_or_user`). This version of the release will be downloaded and sent for security analysis.


__AppCenter latest version of the release__  

To download the latest version of the release you need to use the following parameter: `appcenter_release_id latest`. The command line will look as follows:

```
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name "test_org_or_user" --appcenter_app_name "demo_app" --appcenter_release_id latest --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, the latest available release of the application will be downloaded.

__AppCenter by application version__  

To start the analysis of the application by the known name, owner and version (`version_code` in` Android Manifest`), you need to run the following command:

``` 
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name "test_org_or_user" --appcenter_app_name "demo_app" --appcenter_app_version 31337 --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, in the owner workspace (user or organization `test_org_or_user`) will be found application `demo_app` and will be found a release in which the version of the application `31337` was specified. This version will be downloaded and submitted for security analysis.

### Nexus
To download the application from maven repository you need to know the repository where the mobile application is stored and its group_id, artifact_id and version. To upload mobile application to Nexus you can use [this snippet](https://gist.github.com/Dynamic-Mobile-Security/9730e8eaa1b5d5f7f21e28beb63561a8) for android apk and [this one](https://gist.github.com/Dynamic-Mobile-Security/66daaf526e0109636d8bcdc21fd10779) for iOS ipa.  

Also, you need to select the `distribution_system nexus` and specify the following mandatory parameters:
 * `nexus_url` - http(s) url for Nexus server where the mobile application is located.
 * `nexus_login` - username for Nexus server with permissions to the repository where mobile application is located.
 * `nexus_password` - password for the Nexus server with permissions to the repository where mobile application is located.
 * `nexus_repo_name` - repository name in Nexus where mobile application is located.
 * `nexus_group_id` - group_id of the uploaded mobile application from maven data.
 * `nexus_artifact_id` - artifact_id of the uploaded mobile application from maven data.
 * `nexus_version` - version of the uploaded mobile application from maven data.
 

### Scan types
There are several ways to start scan for android applications: with previously recorded testcase or without it.
 * In first scenario with selected testcase - it will be replayed in the scan execution. 
 * In second scenario without testcase, application will be installed on the device, started, waiting for 30 seconds and then stopped and further analysis will be performed.

#### Start scan with testcase (run previously recorded steps in application)
To start this type of scan you need to specify `id` of previosly recorded testcase in `--testcase_id` parameter:
```
mdast_cli --testcase_id 4 --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```

#### Start scan without testcase 
To start this type of scan don't specify `--testcase_id` parameter:
```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```