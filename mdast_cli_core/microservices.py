"""Client for the microservices installation (Clark facade behind Envoy ExtAuth -> OPA).

Public method names match the monolith client (mDastToken) per ASM-671-01;
routes and payloads follow the Clark facade contract (STGRST-670/671/694/698):

- auth: `Authorization: Bearer <org token>` (org-level opaque token issued in UI);
- all routes live under the same `/rest` prefix as the monolith (base_url ends
  with `/rest` after mdast_scan.py normalization), so the base URL handling is
  shared between both installations;
- tenant comes from the `X-Organization-Id` header injected by the platform,
  the `/organizations/{id}/` URL segment is gone, `company_id` is ignored;
- scans are keyed by application md5 (not application_id) and are created with
  the two-phase model (`fsm_locked=true` + explicit `/scans/{id}/start/`).
"""
import hashlib
import json
import os

import requests

from .base import mDastBase

HTTP_REQUEST_TIMEOUT = 30
HTTP_DOWNLOAD_TIMEOUT = 300
UPLOAD_EXTRA_TIMEOUT = 120


def file_md5(file_path):
    """Lower-case hex md5 of a file (Clark multipart contract requires lower-case)."""
    file_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest().lower()


def extract_error_message(resp):
    """Best-effort human-readable message from Clark error responses.

    /rest routes answer with the monolith envelope {error_code, message};
    the report route answers with the FastAPI envelope {"detail": ...};
    scanyon 429 passes through {"detail": ..., "reasons": [...]}.
    """
    try:
        data = resp.json()
    except ValueError:
        return resp.text
    if isinstance(data, dict):
        if data.get('message'):
            prefix = data.get('error_code')
            message = data['message']
            return f'{prefix}: {message}' if prefix else message
        if data.get('detail') is not None:
            detail = data['detail']
            if not isinstance(detail, str):
                detail = json.dumps(detail, ensure_ascii=False)
            reasons = data.get('reasons')
            if reasons:
                detail = f'{detail} (reasons: {json.dumps(reasons, ensure_ascii=False)})'
            return detail
    return resp.text


class mDastMicroservices(mDastBase):
    """API client for the Clark facade of the microservices installation."""

    def __init__(self, base_url, ci_token, company_id=None, user_agent=None, verify=True):
        super().__init__(base_url)
        # F14: strip trailing slash so f'{self.url}/architectures/' can't produce
        # a double slash (a strict OPA/Envoy path match may 403/404 on '//').
        self.url = base_url.rstrip('/')
        # company_id is accepted for interface parity with mDastToken and ignored:
        # the organization is resolved server-side from the token (X-Organization-Id).
        self.company_id = company_id
        self.current_context = {'company': company_id}
        # F4: TLS verification on by default (org bearer token is a credential);
        # opt out only via MDAST_TLS_VERIFY for self-signed stands.
        self.verify = verify
        self.timeout = HTTP_REQUEST_TIMEOUT
        self.headers = {'Authorization': 'Bearer {0}'.format(ci_token),
                        'Content-Type': 'application/json'}
        if user_agent:
            self.headers['User-Agent'] = user_agent

    def set_headers(self, ci_token):
        self.headers['Authorization'] = 'Bearer {0}'.format(ci_token)

    def _request_headers(self, json_body=True):
        headers = {'Authorization': self.headers['Authorization']}
        if 'User-Agent' in self.headers:
            headers['User-Agent'] = self.headers['User-Agent']
        if json_body:
            headers['Content-Type'] = 'application/json'
        return headers

    # --- preflight ---

    def get_architectures(self):
        return requests.get(f'{self.url}/architectures/',
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)

    def get_engines(self):
        return requests.get(f'{self.url}/engines/',
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)

    def get_testcase(self, testcase_id):
        return requests.get(f'{self.url}/testcases/{testcase_id}/',
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)

    # --- application upload / dedup (STG-4451) ---

    def check_app_md5(self, org_id, md5):
        # org_id is ignored: no organization segment in facade URLs (DEC-694-05)
        return requests.get(f'{self.url}/applications/?md5={md5}',
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)

    def upload_application(self, path, architecture_type=None, upload_timeout=None):
        """Upload via POST /rest/applications/upload_info/.

        Contract (STG-4451 / STG-4450): multipart field `md5` (lower-case hex)
        strictly before `file`; `X-File-Size` header with the exact binary size;
        Content-Length is set by requests (body is fully built, no chunked TE).
        `architecture_type` is accepted for interface parity and not sent:
        the platform parses the binary itself.
        """
        md5 = file_md5(path)
        file_size = os.path.getsize(path)
        headers = self._request_headers(json_body=False)
        headers['X-File-Size'] = str(file_size)
        params = {}
        request_timeout = HTTP_DOWNLOAD_TIMEOUT
        if upload_timeout is not None:
            params['upload_timeout'] = int(upload_timeout)
            request_timeout = int(upload_timeout) + UPLOAD_EXTRA_TIMEOUT
        with open(path, 'rb') as f:
            # ordered list keeps `md5` as the first multipart part (facade requirement)
            multipart = [
                ('md5', (None, md5)),
                ('file', (os.path.split(path)[-1], f, 'application/octet-stream')),
            ]
            return requests.post(f'{self.url}/applications/upload_info/',
                                 headers=headers,
                                 files=multipart,
                                 params=params or None,
                                 verify=self.verify,
                                 timeout=request_timeout)

    # --- scan flow (STG-4475) ---

    def precheck_scan(self, md5, profile_id, testcase_id, scan_type):
        """Gate pre-check before scan creation (DEC-671-05).

        Field is `application_md5` in the scanyon contract (not `md5`).
        scan_type mirrors the create call: MANUAL for a scan without a test case,
        AUTO for a test-case replay.
        """
        data = {
            'application_md5': md5,
            'profile_id': profile_id,
            'type': scan_type,
            'testcase_id': testcase_id,
        }
        return requests.post(f'{self.url}/scans/start/precheck/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=self.verify,
                             timeout=self.timeout)

    def _create_scan(self, project_id, profile_id, app_md5, test_case_id, scan_type):
        # scanyon: AUTO requires testcase_id; a scan without a test case is MANUAL
        # (install/launch/wait/stop semantics, wait=True on the server side).
        # testcase_id key is mandatory in ScanIn even when null.
        data = {
            'md5': app_md5,
            'type': scan_type,
            'testcase_id': test_case_id,
            'fsm_locked': True,
        }
        if project_id:
            data['project_id'] = project_id
        if profile_id:
            data['profile_id'] = profile_id
        return requests.post(f'{self.url}/scans/start/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=self.verify,
                             timeout=self.timeout)

    def create_manual_scan(self, project_id, profile_id, app_md5, arch_id=None):
        # arch_id accepted and ignored (microservices resolve platform from app metadata)
        return self._create_scan(project_id, profile_id, app_md5, None, 'MANUAL')

    def create_auto_scan(self, project_id, profile_id, app_md5, arch_id, test_case_id):
        return self._create_scan(project_id, profile_id, app_md5, test_case_id, 'AUTO')

    def create_appium_scan(self, project_id, profile_id, app_id, arch_id, appium_script_path):
        raise NotImplementedError(
            'Appium scans are not supported on the microservices installation (OOS-671-06)')

    def start_scan(self, dast_id):
        return requests.post(f'{self.url}/scans/{dast_id}/start/',
                             headers=self.headers,
                             verify=self.verify,
                             timeout=self.timeout)

    def stop_scan(self, scan_id):
        return requests.post(f'{self.url}/scans/{scan_id}/stop/',
                             headers=self.headers,
                             verify=self.verify,
                             timeout=self.timeout)

    def get_scan_info(self, scan_id):
        return requests.get(f'{self.url}/scans/{scan_id}/',
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)

    # --- reports (STG-4478) ---

    def _download_report_output(self, dast_id, output):
        return requests.get(f'{self.url}/scans/{dast_id}/report',
                            params={'output': output},
                            allow_redirects=True,
                            headers=self.headers,
                            verify=self.verify,
                            timeout=HTTP_DOWNLOAD_TIMEOUT)

    def download_report(self, dast_id):
        return self._download_report_output(dast_id, 'pdf')

    def download_scan_json_result(self, dast_id):
        return self._download_report_output(dast_id, 'json')
