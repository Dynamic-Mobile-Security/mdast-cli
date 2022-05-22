# App downloader from Google Play and App Store

**Automate the download of mobile applications.**

Dowmload apps from most popular markets automatically 

This script is designed to integrate mobile applications' download in the continuous development process (CI / CD).  

## Install options

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
 * Applications from [Appstore](https://www.apple.com/app-store/)
 * Applications from [Google Play](https://play.google.com/store/apps)
 
### AppStore
To download application from AppStore you need to know application_id or bundle and have **iTunes account** and credentials for it: email and password with 2FA code.  


You need to select the `--distribution_system appstore` and specify mandatory parameters.

To successfully sign in to iTunes, you will need to **obtain and save** the 2fa code for later use.  
When you run the script for the first time, use your email and password, you will get a login error in the console and at this point a two-factor authentication code will come to your device  


<img src="https://user-images.githubusercontent.com/46852358/153638449-6488cf6d-214f-44cb-8265-fe8b79b2614f.png" alt="drawing" width="300"/>  



For the subsequent work of the script without repeating the step with the manual receipt of 2fa code you need to remember the received code, the session with it will be active for 6 months. After that, try to repeat the login with  password and 2FA, formatting it like `password2FA`. You do not need to get new 2fa codes later, this parameter will work for 6 months.   

For example, password is `P@ssword` and 2FA is `742877`, so your parameter `--appstore_password2FA P@ssword742877`.

To get the app_id, go to the app page in the AppStore in your browser, you can extract the required parameter from the url:
![app_id_example](https://user-images.githubusercontent.com/46852358/153639003-f121273a-41ac-415d-aad7-6b2789f77cee.png)  

`appstore_app_id 398129933` in this example. 

Also, you need to select the `distribution_system appstore` and specify the following mandatory parameters:
 * `appstore_app_id` - Application id from AppStore, you can get it on app page from url,   
format: apps.apple.com/app/id{appstore_app_id}
 * `appstore_bundle_id` - same as app_id
 * `appstore_apple_id` - Your email for iTunes login.
 * `appstore_password2FA` - Your password and 2FA code for iTunes login, format: password2FA_code 

You can specify downloaded app file name with an optional parameter

 * `appstore_file_name` - file name for app to be saved with
 
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
 

At the initial run of the script you will get the gsfId and auth token in the script logs, copy and save them. You will need them for a stable and successful execution of the script afterwards  

![gsfid_token_logs](https://user-images.githubusercontent.com/46852358/162791052-fbce7121-1430-49ca-a9b9-68997391abd6.png)  

Using these parameters you will have all parameters for successful downloading applications from Google Play Store:

 * `google_play_package_name` - package name of application you want to download
 * `google_play_gsfid` - The Google Services Framework Identifier (GSF ID)
 * `google_play_auth_token` - Google auth token for access to Google Play API

You can also specify downloaded app file name with an optional parameter

 * `google_play_file_name` - file name for app to be saved with  

You should use either email + pass ("--google_play_email" + "--google_play_password") or gsfid + token ("--google_play_gsfid" + "google_play_auth_token") arguments for mdast_cli script. For the continuous process you need only gsfid and token.

### AppStore launch example
To download application from AppStore, you need to run the following command:
```
 python mdast_cli/mdast_scan.py --distribution_system appstore --appstore_app_id 564177498 --appstore_apple_id ubet******@icloud.com --appstore_password2FA pass*******31******454 --appstore_file_name my_b3st_4pp
```
As a result in the `downloaded_apps` repository will be application with name `my_b3st_4pp.ipa` and manual scan will be started.

### Google Play launch example
To start the initial login for Google Play, you need to run the following command:
```
 python mdast_cli/mdast_scan.py --distribution_system google_play  --google_play_package_name com.instagram.android --google_play_email download*******ly@gmail.com --google_play_password Paaswoord
```
To download app[] from Google Play, you need to run the following command:

```
 python mdast_cli/mdast_scan.py --google_play_package_name com.instagram.android --google_play_gsfid 432******************43 --google_play_auth_token JAgw_2h*************************************8KRaYQ. --google_play_file_name best_apk_d0wnl04d3r
```

As a result in the `downloaded_apps` repository will be application with name `best_apk_d0wnl04d3r.apk` and manual scan will be started.
