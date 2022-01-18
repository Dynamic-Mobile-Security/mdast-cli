# Mobile DAST CI/CD Python script
*Automate the security analysis of mobile applications.*

This script is designed to integrate mobile applications' security analysis in the continuous development process (CI / CD).  
During the execution of the script, the application is sent to the dynamic analysis. The output is a json/pdf file with detailed results.

## Install options

### DockerHub
You can run this script using [docker image](https://hub.docker.com/r/mobilesecurity/mdast_cli):

`docker pull mobilesecurity/mdast_cli:latest`

### From PyPi
It is possible to install a package using pip:

`pip install mdast_cli`

With this method, it is possible to start scanning without specifying the `python` interpreter using the` mdast_cli` command, example:

`mdast_cli -h`

All examples below will use exactly this approach.

### Source
It also supports launching by loading source files and launching the main script directly:

`python3 mdast_cli/mdast_scan.py -h`

With this method of launching, you must additionally install the packages specified in `requirements.txt`

## Launch options
Currently, several launch options are supported:
 * Local file
 * Applications from [HockeyApp](https://hockeyapp.net/)
 * Applications from [AppCenter](https://appcenter.ms)
 * Applications from [Nexus Repository 3.x](https://help.sonatype.com/repomanager3) from maven repo.
 * Applications from [Firebase](https://firebase.google.com/)

## Launch parameters
The launch options depend on the location of the apk file sent for analysis. Also, there are required parameters that must be specified for any type of launch:
 * `url` - network address for system (the path to the root without the final /)
 * `profile_id` - ID of the profile to be analyzed
 * `testcase_id` - ID of the test case to be executed. This is an optional parameter, if not set - manual scan with 20 seconds delay until finish will be executed;
 * `token` - CI/CD access token (refer to our documentation for ways to retrieve the token)
 * `distribution_system` - distribution method for the application; possible values: `file`, `hockeyapp` or `appcenter`. For detailed information refer to the respective sections below.
 * `company_id` - identifier of the company within which the scan will be performed
 * `architecture_id` - identifier of the operating system architecture on which the scan will be performed
 * `nowait` - an optional parameter specifying whether to wait for the scan to complete. If this flag is set, the script will not wait for the scan to complete, but will exit immediately after starting. If the flag is not selected, the script will wait for the completion of the analysis process and generate a report.
 * `summary_report_json_file_name` - an optional parameter defining the name of the json file into which the scanning information in json format is uploaded. If the parameter is absent, the information will not be saved.
 * `pdf_report_file_name` - an optional parameter that specifies the name of the pdf file into which information on scanning in pdf format is uploaded. If the parameter is absent, the report will not be saved.

### Local file launch
This type of launch implies that the application file is located locally.
To select this method at startup, you must specify the parameter `distribution_system file`.  
In this case, the required parameter must specify the path to the file: `file_path`

### HockeyApp
To download an application from the HockeyApp distribution system you need to select the `distribution_system = hockeyapp` parameter.  
Also, you need to specify the following mandatory parameters:

 * `hockey_token` (mandatory parameter) - API access token. Look in the [HockeyApp documentation](https://rink.hockeyapp.net/manage/auth_tokens) how to retrieve it.
 * `hockey_version` (optional parameter) - this parameter downloads the specific version of the application in accordance with its version ID (the `version` field in the [API](https://support.hockeyapp.net/kb/api/api-versions)).   
 If this parameter is not set, the latest available version of the application ("latest") will be downloaded.
 * `hockey_bundle_id` or `hockey_public_id` (mandatory parameter)
    * `hockey_bundle_id` - ID of Android application or, alternatively, the package name (`com.app.example`). This option launches search among all HockeyApp applications and thereafter picks an application with the corresponding ID. API field - [bundle_identifier](https://support.hockeyapp.net/kb/api/api-apps).
    * `hockey_public_id` - ID of an application inside the HockeyApp system. This parameter downloads an application with the corresponding ID. API field - [public_identifier](https://support.hockeyapp.net/kb/api/api-apps)

### AppCenter
To download application from AppCenter distribution system you need to select the `distribution_system appcenter` parameter. Also, you need to specify the following mandatory parameters:
 * `appcenter_token` - API access token. Look in official documentation to [learn how to retrieve it]((https://docs.microsoft.com/en-us/appcenter/api-docs/)).
 * `appcenter_owner_name` - owner of the application. Look in official documentation to learn how to retrieve the [owner name](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name).
 * `appcenter_app_name` - the name of the application in the AppCenter system. Look in official documentation to [learn how to retrieve it](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name)
 * `appcenter_release_id` or `appcenter_app_version`
    * `appcenter_release_id` - ID of the specific release of the application to be downloaded from AppCenter. There is a possibility to select the "latest" value - the [latest available version](https://openapi.appcenter.ms/#/distribute/releases_getLatestByUser) of the application will be downloaded.
    * `appcenter_app_version` - this parameter finds and downloads the specific version of the application in accordance with its version ID (shown in Android Manifest) (the "version" field in the [AppCenter Documentation](https://openapi.appcenter.ms/#/distribute/releases_list))

### Nexus
To download application from maven repository you need to know repository where mobile application is stored and its group_id, artifact_id and version. To upload mobile application to Nexus you can use [this snippet](https://gist.github.com/Dynamic-Mobile-Security/9730e8eaa1b5d5f7f21e28beb63561a8) for android apk and [this one](https://gist.github.com/Dynamic-Mobile-Security/66daaf526e0109636d8bcdc21fd10779) for iOS ipa.  

Also, you need to select the `distribution_system nexus` and specify the following mandatory parameters:
 * `nexus_url` - Http(s) url for Nexus server where mobile application is located.
 * `nexus_login` - username for Nexus server with permissions to repository where mobile application located.
 * `nexus_password` - password for the Nexus server with permissions to repository where mobile application located.
 * `nexus_repo_name` - repository name in Nexus where mobile application is located.
 * `nexus_group_id` - group_id of the uploaded mobile application from maven data.
 * `nexus_artifact_id` - artifact_id of the uploaded mobile application from maven data.
 * `nexus_version` - version of the uploaded mobile application from maven data.


### Firebase
To download application from firebase platform you need to know some cookies for Google SSO authentication and project_id, app_id, app_code, api_key and file_extension parameters from firebase project.  
You need to select the `--distribution_system firebase` and specify mandatory parameters.  

First you should log in via Google SSO to [Firebase](https://console.firebase.google.com/u/0/) and get necessary cookies from your Chrome session local storage(F12 -> Application -> Cookies)  
And copy SID, SSID, APISID, SAPISID, HSID to your launch command. Lifetime of them are 2 years, so you don't have to do it often :)  

Screenshot of cookie storage:
![cookie_storage](https://user-images.githubusercontent.com/46852358/149788352-d453dd78-547f-4989-8132-b94a6f020a81.png)

 * `firebase_SID_cookie` - SID
 * `firebase_HSID_cookie` - HSID
 * `firebase_SSID_cookie` - SSID
 * `firebase_APISID_cookie` - APISID
 * `firebase_SAPISID_cookie` - SAPISID

Now you need project_id, app_id, app_code, api_key to complete parameters for scan. To get them go to:

App Project home page, url looks like `https://console.firebase.google.com/u/0/project/{project_name}}/overview` ->
![app_project](https://user-images.githubusercontent.com/46852358/149789837-2787cb52-355d-4ef0-9440-89053764db78.png)

to `Release & Monitor -> App Distribution` ->
![distr_page](https://user-images.githubusercontent.com/46852358/149791304-2658f1be-9ee0-422e-94ce-59f1ba1858df.png)  

Open network console(F12 -> Network -> Clear) and click `Download`

You will get this request in DevTools:
![download_req](https://user-images.githubusercontent.com/46852358/149792212-512d33ab-2323-45b6-a25c-6a8d817cde1f.png)  

And url will be like:  

`https://firebaseappdistribution-pa.clients6.google.com/v1/projects/{project_id}}/apps/{app_id}/releases/{app_code}:getLatestBinary?alt=json&key={}`  

So, you just extract missing parameters from this request and your launch command for CI/CD mobile applications' security analysis is ready!
Request url will match this pattern, you should extract 4 parameters from url.
`/v1/projects/{project_id}/apps/{app_id}/releases/{app_code}:getLatestBinary?alt=json&key={api_key}`  

 * `firebase_project_id` - project id of your Firebase project
 * `firebase_app_id` - application id
 * `firebase_app_code` - application code
 * `firebase_api_key` - your api key
 * `firebase_app_extension` - your app extension, it can be `apk` for android and `ipa` for iOS

You can specify downloaded app file name with optional parameter

 * `firebase_file_name` - file name for app to be saved with

## Launch examples

### Scan type
There are several ways to start scan: with previously recorded testcase or without it.
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

### Local file

#### Docker launch
After pulling run docker using command like this (all parameters are applied due to distribution_system choice):

```
docker run -it -v {path_to_folder_with_application}:/mdast/files -v {path_to_report_folder}:/mdast/report mobilesecurity/mdast_cli:latest --profile_id 1 --architecture_id 5 --testcase_id 4 --distribution_system file --file_path /mdast/files/{application_file_name} --url "https://saas.mobile.appsec.world" --company_id 1 --token eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1 --summary_report_json_file_name /mdast/report/json-report.json --pdf_report_file_name /mdast/report/pdf-report.pdf
```

Where:
 * `{path_to_folder_with_application}` - absolute path to the folder where build application locating
 * `{path_to_report_folder}` - absolute path to the folder where reports will be generated
 * `{application_file_name}` - full name of the built apk inside the `{path_to_folder_with_application}` folder


#### Standard launch method
To run analysis of a local file:

```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```

As a result, an automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched.

#### Start without waiting for the scan to complete

```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```
As a result, an automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched and the script will finish immediately after starting the scan and will not wait for the end and generate a report.

#### Generating a Summary report in JSON format

```
mdast_cli --distribution_system file --file_path "/files/demo/apk/demo.apk" --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfCvRoENPvLvlPvN_U2mo5VfCvRoENhPlv" --summary_report_json_file_name json-scan-report.json
```
As a result, an automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched, and upon completion of scanning, a JSON report with the total number of defects and brief statistics will be saved.

### HockeyApp by bundle_identifier and version
To run application analysis from a HockeyApp system:

```
mdast_cli --distribution_system hockeyapp --hockey_token 18bc81146d374ba4b1182ed65e0b3aaa --bundle_id com.appsec.demo --hockey_version 31337 --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, an application with the package ID `com.appsec.demo` and version` 31337` will be found on the HockeyApp system. It will be downloaded, and an automated analysis will be performed for it with a profile with `id 2` and a test case with `id 3`.

### HockeyApp with public identifier and the latest available version
To start scanning the latest version of an application in HockeyApp system using the application's public ID:

```
mdast_cli --distribution_system hockeyapp --hockey_token 18bc81146d374ba4b1182ed65e0b3aaa --public_id "1234567890abcdef1234567890abcdef" --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, the latest available version of the application with the unique public ID `1234567890abcdef1234567890abcdef` will be found in HockeyApp system. The application will be downloaded and automatically analyzed using the profile with `id 2` and the test case with `id 3`.

### AppCenter with the release ID
To start scanning an application using its name, the name of the owner and the release ID, the following command should be entered:

```
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name test_org_or_user --appcenter_app_name demo_app --appcenter_release_id 710 --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, the `demo_app` application with release `id 710` will be found among applications of the specified owner (user or organization `test_org_or_user`). This version of the release will be downloaded and sent for security analysis.

To download the latest version of the release you need to use the following parameter: `appcenter_release_id latest`. The command line will look as follows:

```
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name "test_org_or_user" --appcenter_app_name "demo_app" --appcenter_release_id latest --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, the latest available release of the application will be downloaded.

### AppCenter by application version
To start the analysis of the application by the known name, owner and version (`version_code` in` Android Manifest`), you need to run the following command:

```
mdast_cli --distribution_system appcenter --appcenter_token 18bc81146d374ba4b1182ed65e0b3aaa --appcenter_owner_name "test_org_or_user" --appcenter_app_name "demo_app" --appcenter_app_version 31337 --url "https://saas.mobile.appsec.world" --profile_id 2 --testcase_id 3 --company_id 1 --architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hfI6c4VN_U2mo5VfRoENPvJCvpxhLzjHqI0gxqgr2Bs"
```

As a result, in the owner workspace (user or organization `test_org_or_user`) will be found application `demo_app` and will be found a release in which the version of the application `31337` was specified. This version will be downloaded and submitted for security analysis.


### Firebase launch example
To start the manual scan analysis of the application, that was downloaded from Firebase, you need to run the following command:
```
python mdast_cli/mdast_scan.py --profile_id 468 --architecture_id 2 --distribution_system firebase --firebase_project_id 2834204**** --firebase_app_id 1:283***3642:android:8b0a0***56ac40c1a43 --firebase_app_code 2b***sltr0 --firebase_api_key AIzaSyDov*****qKdbj-geRWyzMTrg --firebase_SID_cookie FgiA*****ZiQakQ-_C-5ZaEHvbDMFGkrgriAByQ9P9fv7LfRrYJ5suXgrCwIQBoOjA. --firebase_HSID_cookie AsiL****OjPI --firebase_SSID_cookie A****dwcZk1Z-1pE --firebase_APISID_cookie Z-FmS1aPB****djK/AjmG0h2Hc-GG9g2Ac --firebase_SAPISID_cookie XYR2tnf****0zOt/AEvVZ8JVEuCnE6pxm --url "https://stingray.dev.swordfishsecurity.com/" --company_id 1 --token 2fac9652a2fbe4****9f44af59c3381772f --firebase_file_name your_app_file_name  --firebase_file_extension apk
```
As a result in the `downloaded_apps` repository will be application with name `your_app_file_name.apk` and manual scan will be started.
