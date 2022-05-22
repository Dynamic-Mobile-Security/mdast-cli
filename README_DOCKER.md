# Mobile DAST CI/CD Python script
[![Docker Hub](https://img.shields.io/docker/v/mobilesecurity/mdast_cli?label=docker%20hub)](https://hub.docker.com/repository/docker/mobilesecurity/mdast_cli)
[![PyPi](https://img.shields.io/pypi/v/mdast_cli?color=3)](https://pypi.org/project/mdast-cli/)

**Automate the security analysis of mobile applications.**

This script is designed to integrate mobile applications' security analysis in the continuous development process (CI / CD).  

During the execution of the script, the application is sent to the dynamic analysis. The output is a json/pdf file with detailed results. You can use the local file or download the application from one of the distribution systems. If you download the app, you should have write permissions.

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
Currently, several launch options are supported:
 * Local file
 * Applications from [HockeyApp](https://hockeyapp.net/)
 * Applications from [AppCenter](https://appcenter.ms)
 * Applications from [Nexus Repository 3.x](https://help.sonatype.com/repomanager3) from maven repo.
 * Applications from [Firebase](https://firebase.google.com/)
 * Applications from [Appstore](https://www.apple.com/app-store/)
 * Applications from [Google Play](https://play.google.com/store/apps)

## Launch parameters
The launch options depend on the location of the apk file sent for analysis. Also, there are required parameters that must be specified for any type of launch:
 * `url` - network address for system (the path to the root without the final /)
 * `profile_id` - ID of the profile to be analyzed
 * `testcase_id` - ID of the test case to be executed. This is an optional parameter, if not set - manual scan with 20 seconds delay until finish will be executed;
 * `token` - CI/CD access token (refer to our documentation for ways to retrieve the token)
 * `distribution_system` - distribution method for the application; possible values: `file`, `hockeyapp` or `appcenter`. For detailed information refer to the respective sections below.
 * `company_id` - identifier of the company within which the scan will be performed
 * `architecture_id` - identifier of the operating system architecture on which the scan will be performed
 * `nowait` - an optional parameter specifying whether to wait for the scan to complete. If this flag is set, the script will not wait for the scan to complete but will exit immediately after starting. If the flag is not selected, the script will wait for the completion of the analysis process and generate a report.
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
    * `hockey_bundle_id` - ID of Android application or, alternatively, the package name (`com.app.example`). This option launches a search among all HockeyApp applications and thereafter picks an application with the corresponding ID. API field - [bundle_identifier](https://support.hockeyapp.net/kb/api/api-apps).
    * `hockey_public_id` - ID of an application inside the HockeyApp system. This parameter downloads an application with the corresponding ID. API field - [public_identifier](https://support.hockeyapp.net/kb/api/api-apps)

### AppCenter
To download the application from AppCenter distribution system you need to select the `distribution_system appcenter` parameter. Also, you need to specify the following mandatory parameters:
 * `appcenter_token` - API access token. Look in official documentation to [learn how to retrieve it]((https://docs.microsoft.com/en-us/appcenter/api-docs/)).
 * `appcenter_owner_name` - owner of the application. Look in official documentation to learn how to retrieve the [owner name](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name).
 * `appcenter_app_name` - the name of the application in the AppCenter system. Look in official documentation to [learn how to retrieve it](https://docs.microsoft.com/en-us/appcenter/api-docs/#find-your-app-center-app-name-and-owner-name)
 * `appcenter_release_id` or `appcenter_app_version`
    * `appcenter_release_id` - ID of the specific release of the application to be downloaded from AppCenter. There is a possibility to select the "latest" value - the [latest available version](https://openapi.appcenter.ms/#/distribute/releases_getLatestByUser) of the application will be downloaded.
    * `appcenter_app_version` - this parameter finds and downloads the specific version of the application by its version ID (shown in Android Manifest) (the "version" field in the [AppCenter Documentation](https://openapi.appcenter.ms/#/distribute/releases_list))

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


### Firebase
To download the application from firebase platform you need to know some cookies for Google SSO authentication and project_id, app_id, app_code, api_key and file_extension parameters from firebase project.  
You need to select the `--distribution_system firebase` and specify mandatory parameters.  

First, you should log in via Google SSO to [Firebase](https://console.firebase.google.com/u/0/) and get necessary cookies from your Chrome session local storage(F12 -> Application -> Cookies)  
And copy SID, SSID, APISID, SAPISID, HSID to your launch command. The lifetime of them are 2 years, so you don't have to do it often :)  

Screenshot of cookie storage:  

<img src="https://user-images.githubusercontent.com/46852358/149788352-d453dd78-547f-4989-8132-b94a6f020a81.png" width="1000">


 * `firebase_SID_cookie` - SID
 * `firebase_HSID_cookie` - HSID
 * `firebase_SSID_cookie` - SSID
 * `firebase_APISID_cookie` - APISID
 * `firebase_SAPISID_cookie` - SAPISID

Now you need project_id, app_id, app_code, api_key to complete parameters for the scan. To get them go to:

App Project home page, url looks like this `https://console.firebase.google.com/u/0/project/{project_name}/overview` ->  

<img src="https://user-images.githubusercontent.com/46852358/149789837-2787cb52-355d-4ef0-9440-89053764db78.png" width="1000">

to `Release & Monitor -> App Distribution` ->   

<img src="https://user-images.githubusercontent.com/46852358/149791304-2658f1be-9ee0-422e-94ce-59f1ba1858df.png" width="1000">


Open network console(F12 -> Network -> Clear) and click `Download`

You will get this request in DevTools:  

<img src="https://user-images.githubusercontent.com/46852358/149792212-512d33ab-2323-45b6-a25c-6a8d817cde1f.png" width="1000">

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

### AppStore
To download application from AppStore you need to know application_id and have **iTunes account with installed application** and credentials for it: email and password with 2FA code.  


You need to select the `--distribution_system appstore` and specify mandatory parameters.

This script will not work if the app has not been purchased in your AppStore account. It is the status of the app that is important, it must be confirmed with a fingerprint or password even if it is free. You can check this by making sure your app is in 'My apps' in your AppStore account settings.

To successfully sign in to iTunes, you will need to **obtain and save** the 2fa code for later use.  
When you run the script for the first time, use your email and password, you will get a login error in the console and at this point a two-factor authentication code will come to your device:  


<img src="https://user-images.githubusercontent.com/46852358/153638449-6488cf6d-214f-44cb-8265-fe8b79b2614f.png" alt="drawing" width="200"/>  



For the subsequent work of the script without repeating the step with the manual receipt of 2fa code you need to remember the received code, the session with it will be active for 6 months. After that, try to repeat the login with  password and 2FA, formatting it like `password2FA`. You do not need to get new 2fa codes later, this parameter will work for 6 months.   

For example, password is `P@ssword` and 2FA is `742877`, so your parameter `--appstore_password2FA P@ssword742877`.

To get the app_id, go to the app page in the AppStore in your browser, you can extract the required parameter from the url:  

<img src="https://user-images.githubusercontent.com/46852358/153639003-f121273a-41ac-415d-aad7-6b2789f77cee.png" width="1000">

`appstore_app_id 398129933` in this example. 

Also, you need to select the `distribution_system appstore` and specify the following mandatory parameters:
 * `appstore_app_id` - Application id from AppStore, you can get it on app page from url,   
format: apps.apple.com/app/id{appstore_app_id}
 * `appstore_apple_id` - Your email for iTunes login.
 * `appstore_password2FA` - Your password and 2FA code for iTunes login, format: password2FA_code 

You can specify downloaded app file name with an optional parameter

 * `appstore_file_name` - file name for app to be saved with

If you lost the 2fa code and the login has already been made, the session will be active for a few time without using 2fa, only apple_id + password. You also will not be able to end your session via this script, so for the script to work correctly you need to login again after session expires and save the two-factor authentication code in your notes.  

If there is an error associated with the wrong Apple ID when you start scanning:

  
<img src="https://user-images.githubusercontent.com/46852358/158440208-45868069-d772-4476-a1bf-6508c2bac1eb.jpg" width="300">

or error in logs:

"Logging in to the App Store. To open app, log in with the Apple ID with which you made the purchase."

Then contact the support team to agree on an Apple ID, which will be used for AppStore integration, you will be offered a solution to this problem.

### Google play
To download application from Google Play Store you need **temporary account with 2fa authentication disabled**.  

You should specify the package name of the application you want to download, you can get it directly from the Google Play app page or any other way.


Also, you need to select the `distribution_system google_play`.  

During the initial launch of the script you should specify the mandatory parameters: email + password, after that the application will not be downloaded and the scan will not run, but you will **receive gsfid and token** for google authentication, which you should use later on for the successful Google Play application scan.  

 * `google_play_package_name` - package name of application you want to download
 * `google_play_email` - email of your Google account for first login only
 * `google_play_password` - password of your Google account for login only

You can download app while logging in by email and password with an optional parameter:

 * `google_play_download_with_creds` - app will be downloaded during initial login  

When running the integration of Google Play at the first login from a new ip address it is possible that you will need to confirm your account through the browser, to do this, go to the  [google account verification link](https://accounts.google.com/b/0/DisplayUnlockCaptcha) , login to your temporary account and click on 'Proceed'.  
  
![google_unlock_image](https://user-images.githubusercontent.com/46852358/161290143-05d0d847-2037-4c4f-8187-53d3ffed83ec.png)

After this login will be successful through the script mdast_cli. You can also get a link to solve the problem from the logs of the script.  


At the initial run of the script you will get the gsfId and auth token in the script logs, copy and save them. You will need them for a stable and successful execution of the script afterwards  

![gsfid_token_logs](https://user-images.githubusercontent.com/46852358/162791052-fbce7121-1430-49ca-a9b9-68997391abd6.png)  

Using these parameters you will have all parameters for successful downloading applications from Google Play Store:

 * `google_play_package_name` - package name of application you want to download
 * `google_play_gsfid` - The Google Services Framework Identifier (GSF ID)
 * `google_play_auth_token` - Google auth token for access to Google Play API

You can also specify downloaded app file name with an optional parameter

 * `google_play_file_name` - file name for app to be saved with  

You should use either email + pass ("--google_play_email" + "--google_play_password") or gsfid + token ("--google_play_gsfid" + "google_play_auth_token") arguments for mdast_cli script. For the continuous process you need only gsfid and token.




### Launch example

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
docker run -it -v {path_to_folder_with_application}:/mdast/files -v {path_to_report_folder}:/mdast/report mobilesecurity/mdast_cli:latest --distribution_system file --file_path /mdast/files/demo.apk --url "https://saas.mobile.appsec.world" --profile_id 1 --testcase_id 4 --company_id 1 - architecture_id 1 --token "eyJ0eXA4OiJKA1QiLbJhcGciO5JIU4I1NiJ1.eyJzdaJqZWNcX2lkIj53LCJle5AiOjf1OTM5OTU3MjB1.hrI6c4VN_U2mo5VjHvRoENPv2"
```

As a result, automated analysis of the `demo.apk` application with a profile with` id` 1 will be launched and a test case with `id` 4 will be launched.


If you want to find more launch examples of the mdast_cli script please go to the [github readme](https://github.com/Dynamic-Mobile-Security/mdast-cli#launch-examples). Due to word limit on the dockerhub we can't provide a full description of the examples here.