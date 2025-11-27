# Mobile DAST CI/CD

**Python script for automating security analysis of mobile applications.**

[![Docker Hub](https://img.shields.io/docker/v/mobilesecurity/mdast_cli?label=docker%20hub)](https://hub.docker.com/repository/docker/mobilesecurity/mdast_cli)
[![PyPi](https://img.shields.io/pypi/v/mdast_cli?color=3)](https://pypi.org/project/mdast-cli/)
![GitHub issues](https://img.shields.io/github/issues-raw/Dynamic-Mobile-Security/mdast-cli)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/Dynamic-Mobile-Security/mdast-cli)

## Overview

This script is designed to integrate mobile applications' security analysis into the continuous development process (CI/CD). It supports downloading applications from various distribution systems and performing dynamic security analysis (DAST).

### Key Features

- **Multiple Distribution Systems**: Support for 9+ distribution platforms (Google Play, AppStore, Firebase, Nexus, etc.)
- **Download Only Mode**: Download applications without scanning for testing or manual analysis
- **Automated Scanning**: Full integration with DAST scanning platform
- **Multiple Report Formats**: Generate JSON and PDF reports
- **CI/CD Ready**: Designed for seamless integration into CI/CD pipelines
- **Docker Support**: Pre-built Docker images for easy deployment

### What It Does

1. **Downloads** mobile applications (APK/IPA) from supported distribution systems
2. **Uploads** applications to the DAST scanning platform
3. **Executes** security scans (manual or automated with testcases)
4. **Generates** detailed security reports in JSON and/or PDF formats
5. **Returns** structured output suitable for CI/CD integration

---

## Table of Contents

* [Installation](#installation)
  * [Docker (Recommended)](#docker-recommended)
  * [PyPI Package](#pypi-package)
  * [From Source](#from-source)
* [Quick Start](#quick-start)
* [Usage Modes](#usage-modes)
  * [Download Only Mode](#download-only-mode)
  * [Scan Mode](#scan-mode)
* [Distribution Systems](#distribution-systems)
  * [Local File](#local-file)
  * [Google Play](#google-play)
  * [AppStore](#appstore)
  * [Firebase](#firebase)
  * [Nexus Repository](#nexus-repository)
  * [Nexus2 Repository](#nexus2-repository)
  * [RuStore](#rustore)
  * [AppGallery](#appgallery)
  * [RuMarket](#rumarket)
* [Scan Configuration](#scan-configuration)
  * [Scan Types](#scan-types)
  * [Architecture Selection](#architecture-selection)
  * [Profile Management](#profile-management)
* [Reports](#reports)
  * [JSON Summary Report](#json-summary-report)
  * [PDF Report](#pdf-report)
  * [CR Report](#cr-report)
* [Advanced Features](#advanced-features)
  * [Non-blocking Scans](#non-blocking-scans)
  * [Long-running Scans](#long-running-scans)
  * [Appium Integration](#appium-integration)
* [Troubleshooting](#troubleshooting)
* [Exit Codes](#exit-codes)
* [Examples](#examples)

---

## Installation

### Docker (Recommended)

The easiest way to use `mdast_cli` is via Docker:

```bash
# Pull the latest image
docker pull mobilesecurity/mdast_cli:latest

# Run with volume mounts for files and reports
docker run -it \
  -v /path/to/apps:/mdast/files \
  -v /path/to/reports:/mdast/report \
  mobilesecurity/mdast_cli:latest \
  --distribution_system file \
  --file_path /mdast/files/app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1
```

**Benefits:**
- No Python environment setup required
- All dependencies pre-installed
- Consistent execution environment
- Easy CI/CD integration

### PyPI Package

Install from PyPI using pip:

```bash
pip install mdast_cli
```

After installation, you can use the `mdast_cli` command directly:

```bash
mdast_cli --help
```

**Note:** You may need to install additional system dependencies depending on your distribution system choice (e.g., `apkeep` for Google Play).

### From Source

**Requirements:**
- Python 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported)

Clone the repository and install dependencies:

```bash
git clone https://github.com/Dynamic-Mobile-Security/mdast-cli.git
cd mdast-cli
pip install -r requirements.txt
```

Then run the script directly:

```bash
python3 mdast_cli/mdast_scan.py --help
```

---

## Quick Start

### Download an Application

```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email user@example.com \
  --google_play_aas_token "YOUR_AAS_TOKEN"
```

### Run a Security Scan

```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --testcase_id 4 \
  --summary_report_json_file_name report.json
```

---

## Usage Modes

### Download Only Mode

Use the `--download_only` (or `-d`) flag to download applications without scanning:

```bash
mdast_cli -d --distribution_system google_play --google_play_package_name com.example.app ...
```

**Output:**
- Downloads the application to the specified `--download_path` (default: `downloaded_apps/`)
- Prints `DOWNLOAD_PATH=/path/to/app.apk` for CI/CD parsing
- Exits immediately after download

**Use Cases:**
- Testing download functionality
- Manual application analysis
- CI/CD pipelines that handle scanning separately

### Scan Mode

Without `--download_only`, the script will:
1. Download the application (if not using `file` distribution)
2. Upload to the DAST platform
3. Start a security scan
4. Wait for completion (unless `--nowait` is set)
5. Generate reports (if specified)

---

## Distribution Systems

### Local File

Use a local APK/IPA file for scanning.

**Required Parameters:**
- `--distribution_system file`
- `--file_path <path>` - Absolute or relative path to the application file

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path /path/to/app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1
```

**Docker Example:**
```bash
docker run -it \
  -v /host/path/to/apps:/mdast/files \
  -v /host/path/to/reports:/mdast/report \
  mobilesecurity/mdast_cli:latest \
  --distribution_system file \
  --file_path /mdast/files/app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --summary_report_json_file_name /mdast/report/report.json
```

---

### Google Play

Download applications from Google Play Store using `apkeep`.

**Prerequisites:**
1. Install `apkeep`:
   ```bash
   # Using Rust (requires Rust toolchain)
   cargo install apkeep
   
   # Or download prebuilt binary from:
   # https://github.com/EFForg/apkeep/releases
   # Place binary in your PATH
   ```

2. Obtain authentication:
   - **Option A**: OAuth2 token (recommended for first-time setup)
   - **Option B**: AAS token (reuse from previous runs)

**Required Parameters:**
- `--distribution_system google_play`
- `--google_play_package_name <package>` - Package name (e.g., `com.instagram.android`)
- `--google_play_email <email>` - Google account email
- **Either:**
  - `--google_play_oauth2_token <token>` - OAuth2 token to fetch AAS automatically
  - `--google_play_aas_token <token>` - Direct AAS token (from previous run)

**Optional Parameters:**
- `--google_play_file_name <name>` - Custom filename for downloaded app
- `--google_play_proxy <proxy>` - Proxy configuration (e.g., `socks5://user:pass@host:port`)

**Getting Package Name:**
- Visit the app page on Google Play
- Package name is visible in the URL: `play.google.com/store/apps/details?id=<PACKAGE_NAME>`
- Or check the app's page source

**Authentication Flow:**

1. **First Run (OAuth2):**
   ```bash
   mdast_cli -d \
     --distribution_system google_play \
     --google_play_package_name com.example.app \
     --google_play_email user@example.com \
     --google_play_oauth2_token "ya29.a0AVvZ..."
   ```
   - The script will fetch an AAS token automatically
   - **Save the AAS token from logs** for future runs
   - Look for `AAS token: aas_et/...` in the output

2. **Subsequent Runs (AAS Token):**
   ```bash
   mdast_cli -d \
     --distribution_system google_play \
     --google_play_package_name com.example.app \
     --google_play_email user@example.com \
     --google_play_aas_token "aas_et/AKppINZUCsnVs80yu3k4ZpiApuOlHlOnxSlwNNMOPjomkWDDbNi1SKd0PRTbOFSS6TNLQFlY70SIrUoxUnababWUcBXuhuVdpmrVUvff5etUCWqToxpRkHV8jf4RLcwX56AMkGhlslqrY4hrAH28-yCyOf9FFeLnhCo9p3ydbRrT5at3Le3Tnc-0CPILroJ_NldfLpDeQvBcj2BM_wBM-Tc"
   ```

**Important Notes:**
- Use a **temporary Google account with 2FA disabled** (recommended)
- Split APKs are automatically packaged into a ZIP archive
- Python 3.9 or higher required (3.9, 3.10, 3.11, 3.12 supported)
- AAS tokens are long-lived but may expire; keep OAuth2 token as backup

**Example with Scan:**
```bash
mdast_cli \
  --distribution_system google_play \
  --google_play_package_name com.instagram.android \
  --google_play_email user@example.com \
  --google_play_aas_token "YOUR_AAS_TOKEN" \
  --google_play_file_name instagram_latest \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --testcase_id 4 \
  --summary_report_json_file_name report.json
```

---

### AppStore

Download iOS applications (.ipa) from the App Store.

**Prerequisites:**
- iTunes account with valid credentials
- 2FA enabled on the Apple ID
- Application ID or Bundle ID

**Required Parameters:**
- `--distribution_system appstore`
- **Either:**
  - `--appstore_app_id <id>` - Application ID from App Store URL
  - `--appstore_bundle_id <bundle>` - Bundle identifier
- `--appstore_apple_id <email>` - iTunes account email
- `--appstore_password <password>` - iTunes account password
- `--appstore_2FA <code>` - 6-digit 2FA code

**Optional Parameters:**
- `--appstore_file_name <name>` - Custom filename for downloaded IPA

**Getting App ID:**
1. Visit the app page in App Store (web or app)
2. Extract ID from URL: `apps.apple.com/app/id{APP_ID}`
3. Example: URL contains `id398129933` → use `398129933`

**2FA Setup (First Time):**
1. Run the script with email and password
2. You'll receive a 2FA code on your device
3. Use the code with `--appstore_2FA`
4. **Save the combined password+2FA** format for 6 months: `password2FA` (e.g., `P@ssword742877`)

**Deprecated Parameter:**
- `--appstore_password2FA` - Will be removed on 01.05.2023. Use separate `--appstore_password` and `--appstore_2FA` instead.

**Example:**
```bash
mdast_cli \
  --distribution_system appstore \
  --appstore_app_id 564177498 \
  --appstore_apple_id user@icloud.com \
  --appstore_password "YourPassword" \
  --appstore_2FA 123456 \
  --appstore_file_name my_app \
  --url "https://saas.mobile.appsec.world" \
  --company_id 2 \
  --token "YOUR_TOKEN" \
  --profile_id 1246 \
  --architecture_id 3
```

**Troubleshooting:**
- **"Wrong Apple ID" error**: Contact support to coordinate the Apple ID for AppStore integration
- **Session expired**: Re-authenticate and save the new 2FA code
- **Login errors**: Ensure 2FA is enabled and code is current (6-digit format)

**Note:** This integration uses [ipatool](https://github.com/majd/ipatool) - thanks to all contributors!

---

### Firebase

Download applications from Firebase App Distribution.

**Prerequisites:**
1. Firebase project with App Distribution enabled
2. Service Account with `cloud-platform` scope
3. JSON key file for the Service Account

**Required Parameters:**
- `--distribution_system firebase`
- `--firebase_project_number <number>` - Project number (integer)
- `--firebase_app_id <id>` - Application ID (format: `1:PROJECT:android:APP_ID`)
- `--firebase_account_json_path <path>` - Path to Service Account JSON key file
- `--firebase_file_extension <ext>` - File extension: `apk` or `ipa`

**Optional Parameters:**
- `--firebase_file_name <name>` - Custom filename (defaults to version name)

**Finding Project Number:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click Settings (gear icon) → Project settings
4. Find "Project number" in the General tab

**Finding App ID:**
1. In Project settings, scroll to "Your apps"
2. Find your app and copy the App ID
3. Format: `1:PROJECT_NUMBER:android:APP_ID` or `1:PROJECT_NUMBER:ios:APP_ID`

**Creating Service Account:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service accounts**
3. Create a new Service Account or use existing
4. Grant the `Cloud Platform` scope (`/auth/cloud-platform`)
5. Create and download a JSON key file
6. Save the file securely (keep it out of version control!)

**Example:**
```bash
mdast_cli -d \
  --distribution_system firebase \
  --firebase_project_number 1231231337 \
  --firebase_app_id "1:1337:android:123123" \
  --firebase_account_json_path /path/to/service_account.json \
  --firebase_file_extension apk \
  --firebase_file_name my_app
```

**Security Note:** Never commit Service Account JSON files to version control. Use environment variables or secure secret management in CI/CD.

---

### Nexus Repository

Download applications from Nexus Repository Manager 3.x (Maven repository).

**Required Parameters:**
- `--distribution_system nexus`
- `--nexus_url <url>` - Nexus server URL (e.g., `https://nexus.example.com`)
- `--nexus_login <username>` - Nexus username
- `--nexus_password <password>` - Nexus password
- `--nexus_repo_name <name>` - Repository name
- `--nexus_group_id <group>` - Maven group ID
- `--nexus_artifact_id <artifact>` - Maven artifact ID
- `--nexus_version <version>` - Application version

**Maven Coordinates:**
The script uses standard Maven coordinates to locate artifacts:
- Format: `group_id:artifact_id:version`
- Example: `com.example:myapp:1.0.0`

**Uploading to Nexus:**
See these gists for uploading apps to Nexus:
- [Android APK upload script](https://gist.github.com/Dynamic-Mobile-Security/9730e8eaa1b5d5f7f21e28beb63561a8)
- [iOS IPA upload script](https://gist.github.com/Dynamic-Mobile-Security/66daaf526e0109636d8bcdc21fd10779)

**Example:**
```bash
mdast_cli -d \
  --distribution_system nexus \
  --nexus_url https://nexus.example.com \
  --nexus_login myuser \
  --nexus_password mypass \
  --nexus_repo_name releases \
  --nexus_group_id com.example \
  --nexus_artifact_id myapp \
  --nexus_version 1.0.0
```

---

### Nexus2 Repository

Download applications from Nexus Repository Manager 2.x.

**Required Parameters:**
- `--distribution_system nexus2`
- `--nexus2_url <url>` - Nexus2 server URL
- `--nexus2_login <username>` - Nexus2 username
- `--nexus2_password <password>` - Nexus2 password
- `--nexus2_repo_name <name>` - Repository name
- `--nexus2_group_id <group>` - Maven group ID
- `--nexus2_artifact_id <artifact>` - Maven artifact ID
- `--nexus2_version <version>` - Application version
- `--nexus2_extension <ext>` - File extension (e.g., `apk`, `ipa`)

**Optional Parameters:**
- `--nexus2_file_name <name>` - Custom filename

**Example:**
```bash
mdast_cli -d \
  --distribution_system nexus2 \
  --nexus2_url http://nexus:8081/nexus/ \
  --nexus2_login admin \
  --nexus2_password admin123 \
  --nexus2_repo_name releases \
  --nexus2_group_id com.example \
  --nexus2_artifact_id myapp \
  --nexus2_version 1.337 \
  --nexus2_extension apk \
  --nexus2_file_name my_app
```

---

### RuStore

Download Android applications from [RuStore](https://rustore.ru/) (Russian app store).

**Required Parameters:**
- `--distribution_system rustore`
- `--rustore_package_name <package>` - Package name (e.g., `ru.example.app`)

**Getting Package Name:**
- Visit the app page on RuStore
- Package name is typically visible in the URL or app details

**Example:**
```bash
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name ru.example.app
```

---

### AppGallery

Download applications from [Huawei AppGallery](https://appgallery.huawei.com/).

**Required Parameters:**
- `--distribution_system appgallery`
- `--appgallery_app_id <id>` - Application ID from AppGallery

**Optional Parameters:**
- `--appgallery_file_name <name>` - Custom filename

**Getting App ID:**
1. Visit the app page in AppGallery
2. Extract ID from URL: `appgallery.huawei.com/app/{APP_ID}`
3. Example: URL contains `C101184875` → use `C101184875`

**Example:**
```bash
mdast_cli -d \
  --distribution_system appgallery \
  --appgallery_app_id C123456789 \
  --appgallery_file_name huawei_app
```

---

### RuMarket

Download Android applications from [RuMarket](https://ruplay.market/apps/) (Russian app store).

**Required Parameters:**
- `--distribution_system rumarket`
- `--rumarket_package_name <package>` - Package name

**Example:**
```bash
mdast_cli -d \
  --distribution_system rumarket \
  --rumarket_package_name com.example.app
```

---

## Scan Configuration

### Scan Types

#### Manual Scan (Default)

When `--testcase_id` is **not** specified:
- Application is installed on the device
- Application is launched automatically
- Waits 30 seconds for user interaction
- Application is stopped
- Security analysis is performed

**Use Case:** Quick security checks, initial assessments

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1
  # No --testcase_id = manual scan
```

#### Automated Scan with Testcase

When `--testcase_id` is specified:
- Previously recorded testcase is replayed
- All recorded user interactions are executed
- Comprehensive security analysis is performed

**Use Case:** Deep security analysis, regression testing, CI/CD integration

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --testcase_id 4  # Automated scan with testcase #4
```

### Architecture Selection

**Parameter:** `--architecture_id <id>`

Select the target architecture/OS version for scanning:
- If not specified, defaults to Android 11 or iOS 14 (depending on file type)
- Use specific architecture ID for testing on different OS versions
- Available architectures depend on your DAST platform configuration

**Example:**
```bash
mdast_cli ... --architecture_id 5  # Use architecture ID 5
```

### Profile Management

**Parameter:** `--profile_id <id>` (optional)

- If **not specified**: A new profile is created automatically
- If **specified**: Uses existing profile with the given ID
- Profiles contain device configuration, app settings, and scan parameters

**Auto-create in Existing Project:**
```bash
mdast_cli ... --project_id 10  # Create profile in project #10
```

---

## Reports

### JSON Summary Report

Generate a structured JSON report with scan summary and statistics.

**Parameter:** `--summary_report_json_file_name <filename>`

**Output Format:**
- Total number of vulnerabilities
- Vulnerability breakdown by severity
- Scan metadata (timestamp, duration, etc.)
- Application information

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --summary_report_json_file_name scan_results.json
```

**Use Case:** CI/CD integration, automated reporting, data analysis

### PDF Report

Generate a detailed PDF report with full scan results.

**Parameter:** `--pdf_report_file_name <filename>`

**Output Format:**
- Detailed vulnerability descriptions
- Screenshots and evidence
- Remediation recommendations
- Executive summary

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --pdf_report_file_name detailed_report.pdf
```

**Use Case:** Compliance reporting, stakeholder presentations, documentation

### CR Report

Generate a CR (Change Request) report in HTML format.

**Required Parameters (when `--cr_report` is set):**
- `--cr_report` - Enable CR report generation
- `--stingray_login <login>` - Stingray platform login
- `--stingray_password <password>` - Stingray platform password

**Optional Parameters:**
- `--organization_name <name>` - Organization name (default: "ООО Стингрей Технолоджиз")
- `--engineer_name <name>` - Engineer name
- `--controller_name <name>` - Controller name
- `--use_ldap` - Use LDAP authentication
- `--authority_server_id <id>` - Authority server ID
- `--cr_report_path <path>` - Output file path (default: `stingray-CR-report.html`)

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1337 \
  --architecture_id 3 \
  --cr_report \
  --stingray_login user@example.com \
  --stingray_password "password" \
  --organization_name "My Company" \
  --engineer_name "John Doe" \
  --controller_name "Jane Smith" \
  --cr_report_path custom-report.html
```

---

## Advanced Features

### Non-blocking Scans

Use `--nowait` (or `-nw`) to start a scan and exit immediately without waiting for completion.

**Use Case:**
- Long-running scans
- Fire-and-forget scenarios
- CI/CD pipelines that poll for results separately

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --nowait  # Exit immediately after starting scan
```

**Note:** Reports will not be generated when using `--nowait`. Poll the API separately for results.

### Long-running Scans

Use `--long_wait` to extend the maximum wait time to 1 week (instead of default timeout).

**Use Case:**
- Very long testcases
- Deep analysis scenarios
- Extended monitoring periods

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --testcase_id 4 \
  --long_wait  # Wait up to 1 week for completion
```

### Appium Integration

Use `--appium_script_path` to provide a custom Appium script for automated testing.

**Parameter:** `--appium_script_path <path>`

**Use Case:**
- Custom test automation
- Integration with existing Appium test suites
- Advanced interaction scenarios

**Example:**
```bash
mdast_cli \
  --distribution_system file \
  --file_path app.apk \
  --url "https://saas.mobile.appsec.world" \
  --company_id 1 \
  --token "YOUR_TOKEN" \
  --profile_id 1 \
  --appium_script_path /path/to/appium_script.py
```

### Download Path Configuration

**Parameter:** `--download_path <path>` (or `-p <path>`)

Specify where downloaded applications should be saved.

- **Default:** `downloaded_apps/`
- Can be absolute or relative path
- Directory is created automatically if it doesn't exist

**Example:**
```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email user@example.com \
  --google_play_aas_token "TOKEN" \
  --download_path /custom/path/to/apps
```

---

## Troubleshooting

### Common Issues

#### Google Play Authentication Errors

**Problem:** `DF-DFERH-01` error or authentication failures

**Solutions:**
1. Ensure `apkeep` is installed and in PATH: `apkeep --version`
2. Verify OAuth2 token is valid and not expired
3. Use a temporary Google account with 2FA disabled
4. Check that AAS token format is correct (starts with `aas_et/`)

#### AppStore Login Issues

**Problem:** "Wrong Apple ID" or login failures

**Solutions:**
1. Ensure 2FA is enabled on the Apple ID
2. Use the 6-digit 2FA code (not the longer backup code)
3. Format password+2FA correctly: `password2FA` (e.g., `P@ssword742877`)
4. Contact support if Apple ID needs to be whitelisted
5. Re-authenticate if session expired (sessions last ~6 months)

#### Firebase Service Account Errors

**Problem:** Authentication or permission errors

**Solutions:**
1. Verify Service Account JSON file path is correct
2. Ensure Service Account has `cloud-platform` scope enabled
3. Check that Service Account has access to Firebase App Distribution
4. Verify project number and app ID format
5. Ensure JSON file is valid (not corrupted)

#### Network/Timeout Issues

**Problem:** Downloads fail or time out

**Solutions:**
1. Check network connectivity
2. Verify distribution system URLs are accessible
3. Use `--google_play_proxy` for Google Play if behind firewall
4. Increase timeout values (if configurable)
5. Check firewall/proxy settings

#### File Not Found Errors

**Problem:** Application file not found after download

**Solutions:**
1. Check `--download_path` directory permissions
2. Verify disk space is available
3. Check file system permissions
4. Review download logs for errors
5. Ensure distribution system returned valid file

### Getting Help

1. **Check Logs:** Review console output for detailed error messages
2. **Verify Parameters:** Use `--help` to see all available options
3. **Test Download Only:** Use `-d` flag to isolate download issues
4. **Contact Support:** Reach out with:
   - Full command used
   - Error messages
   - Distribution system and parameters (redact sensitive data)
   - Log output

---

## Exit Codes

The script uses standardized exit codes for CI/CD integration:

| Code | Constant | Description |
|------|----------|-------------|
| 0 | `SUCCESS` | Operation completed successfully |
| 1 | `INVALID_ARGS` | Invalid command-line arguments |
| 2 | `AUTH_ERROR` | Authentication failed |
| 3 | `DOWNLOAD_FAILED` | Application download failed |
| 4 | `NETWORK_ERROR` | Network/connection error |
| 5 | `SCAN_FAILED` | Scan execution or upload failed |

**Example CI/CD Usage:**
```bash
#!/bin/bash
mdast_cli --distribution_system file --file_path app.apk ...
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Scan completed successfully"
elif [ $EXIT_CODE -eq 3 ]; then
  echo "Download failed - check distribution system"
  exit 1
else
  echo "Scan failed with code $EXIT_CODE"
  exit 1
fi
```

---

## Examples

### Complete CI/CD Pipeline Example

```bash
#!/bin/bash
set -e

# Download application
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email ci@example.com \
  --google_play_aas_token "$GOOGLE_PLAY_AAS_TOKEN" \
  --download_path ./artifacts

# Extract download path from output
DOWNLOAD_PATH=$(mdast_cli -d ... 2>&1 | grep "DOWNLOAD_PATH=" | cut -d'=' -f2)

# Run security scan
mdast_cli \
  --distribution_system file \
  --file_path "$DOWNLOAD_PATH" \
  --url "$DAST_URL" \
  --company_id "$COMPANY_ID" \
  --token "$DAST_TOKEN" \
  --profile_id "$PROFILE_ID" \
  --testcase_id "$TESTCASE_ID" \
  --summary_report_json_file_name ./reports/scan_results.json \
  --pdf_report_file_name ./reports/scan_results.pdf

# Check results
if [ -f ./reports/scan_results.json ]; then
  CRITICAL_COUNT=$(jq '.vulnerabilities.critical' ./reports/scan_results.json)
  if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "Critical vulnerabilities found!"
    exit 1
  fi
fi
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  mdast-scan:
    image: mobilesecurity/mdast_cli:latest
    volumes:
      - ./apps:/mdast/files
      - ./reports:/mdast/report
    environment:
      - DAST_URL=https://saas.mobile.appsec.world
      - COMPANY_ID=1
      - TOKEN=${DAST_TOKEN}
    command:
      - --distribution_system
      - file
      - --file_path
      - /mdast/files/app.apk
      - --url
      - ${DAST_URL}
      - --company_id
      - ${COMPANY_ID}
      - --token
      - ${TOKEN}
      - --profile_id
      - "1"
      - --summary_report_json_file_name
      - /mdast/report/results.json
```

### Multi-Distribution Example

```bash
# Test multiple distribution systems
for DIST in google_play appstore firebase; do
  echo "Testing $DIST..."
  mdast_cli -d \
    --distribution_system "$DIST" \
    --download_path "./downloads/$DIST" \
    # ... distribution-specific parameters
done
```

---

## Additional Resources

- **Docker Hub:** https://hub.docker.com/r/mobilesecurity/mdast_cli
- **PyPI Package:** https://pypi.org/project/mdast-cli/
- **GitHub Repository:** https://github.com/Dynamic-Mobile-Security/mdast-cli
- **apkeep (Google Play):** https://github.com/EFForg/apkeep
- **ipatool (AppStore):** https://github.com/majd/ipatool

---

## License

See LICENSE file for details.

---

## Support

For issues, questions, or contributions, please visit the GitHub repository or contact support.

**Note:** This documentation is maintained alongside the codebase. For the latest information, always refer to the version-specific documentation or the `--help` command output.
