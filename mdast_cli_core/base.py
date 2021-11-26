import json
import os
from abc import abstractmethod

import requests


class mDastBase:
    def __init__(self, base_url):
        self.headers = {}
        self.current_context = {}
        self.url = base_url

    @abstractmethod
    def set_headers(self, ci_token):
        pass

    def get_current_user_info(self):
        current_user_info_resp = requests.get(f'{self.url}/currentuser/',
                                              headers=self.headers,
                                              verify=False)
        self.current_context = current_user_info_resp.json()
        return current_user_info_resp

    def set_user_language(self, login, lang):
        data = {
            'username': login,
            'language': lang
        }
        set_language_resp = requests.patch(f'{self.url}/currentuser/',
                                           headers=self.headers,
                                           data=json.dumps(data),
                                           verify=False)
        assert set_language_resp.status_code == 200

    def get_projects(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/projects/',
                            headers=self.headers,
                            verify=False)

    def get_projects_by_org_id(self, org_id):
        return requests.get(f'{self.url}/organizations/{org_id}/projects/',
                            headers=self.headers,
                            verify=False)

    def create_project(self, project_info, arch_type):
        data = {
            'name': project_info['name'],
            'description': project_info['description'],
            'architecture_type': arch_type
        }
        return requests.post(f'{self.url}/organizations/{self.current_context["company"]}/projects/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def create_project_for_organization(self, org_id, project_info, arch_type):
        data = {
            'name': project_info['name'],
            'description': project_info['description'],
            'architecture_type': arch_type
        }
        return requests.post(f'{self.url}/organizations/{org_id}/projects/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def get_users(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/users',
                            headers=self.headers,
                            verify=False)

    def get_users_by_org(self, org_id):
        return requests.get(f'{self.url}/organizations/{org_id}/users',
                            headers=self.headers,
                            verify=False)

    def get_user_info(self, user_id):
        return requests.get(f'{self.url}/users/{user_id}/',
                            headers=self.headers,
                            verify=False)

    def create_user(self, org_id, user_data, role):
        data = {
            'username': user_data['username'],
            'password': user_data['password'],
            'role': role
        }
        return requests.post(f'{self.url}/organizations/{org_id}/users/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def create_user_by_superadmin(self, user_id, username, org_id, role, is_active, change_password,
                                  accepted_eula, accepted_confidential):
        data = {
            'username': username,
            'role': role,
            'is_active': is_active,
            'change_password': change_password,
            'org_id': org_id,
            'accepted_eula': accepted_eula,
            'accepted_confidential': accepted_confidential
        }
        return requests.put(f'{self.url}/users/{user_id}/', headers=self.headers, data=json.dumps(data), verify=False)

    def delete_user(self, user_id):
        return requests.delete(f'{self.url}/users/{user_id}/',
                               headers=self.headers,
                               verify=False)

    def update_username(self, user_id, username):
        data = {
            'username': username
        }
        return requests.patch(f'{self.url}/users/{user_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def patch_user(self, user_id, username, role, is_active, change_password, accepted_eula, accepted_confidential):
        data = {
            'username': username,
            'role': role,
            'is_active': is_active,
            'change_password': change_password,
            'accepted_eula': accepted_eula,
            'accepted_confidential': accepted_confidential
        }
        return requests.patch(f'{self.url}/users/{user_id}/', headers=self.headers, data=json.dumps(data), verify=False)

    def accept_agreements(self, accept_eula, accept_confidential):
        data = {
            'accepted_eula': accept_eula,
            'accepted_confidential': accept_confidential
        }
        return requests.patch(f'{self.url}/currentuser/accept_agreements/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def change_user_organisation(self, user_data, new_org_id):
        data = {
            'username': user_data['username'],
            'company': new_org_id
        }
        user_id = user_data['id']
        return requests.patch(f'{self.url}/users/{user_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def get_project(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/',
                            headers=self.headers,
                            verify=False)

    def delete_project(self, project_id):
        return requests.delete(f'{self.url}/projects/{project_id}/',
                               headers=self.headers,
                               verify=False)

    def get_profiles_for_project(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/profiles/',
                            headers=self.headers,
                            verify=False)

    def get_profile(self, profile_id):
        return requests.get(f'{self.url}/profiles/{profile_id}/',
                            headers=self.headers,
                            verify=False)

    def get_profile_settings(self, profile_id):
        return requests.get(f'{self.url}/profiles/{profile_id}/settings/',
                            headers=self.headers,
                            verify=False)

    def create_profile_for_project(self, project_id, profile_info):
        data = {
            'name': profile_info['name'],
            'description': profile_info['description'],
            'project': project_id
        }
        return requests.post(f'{self.url}/projects/{project_id}/profiles/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def update_testcase_for_project(self, project_id, test_case_id, updated_test_case_info):
        data = {
            'name': updated_test_case_info['name'],
            'description': updated_test_case_info['description'],
            'project': project_id
        }
        return requests.patch(f'{self.url}/testcases/{test_case_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def update_profile_for_project(self, project_id, profile_id, updated_profile_info):
        data = {
            'name': updated_profile_info['name'],
            'description': updated_profile_info['description'],
            'project': project_id
        }
        return requests.patch(f'{self.url}/profiles/{profile_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def update_project(self, project_id, updated_project_info):
        data = {
            'name': updated_project_info['name'],
            'description': updated_project_info['description'],
            'project': project_id
        }
        return requests.patch(f'{self.url}/projects/{project_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def delete_profile(self, profile_id):
        return requests.delete(f'{self.url}/profiles/{profile_id}/',
                               headers=self.headers,
                               verify=False)

    def get_all_scans(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/dasts/',
                            headers=self.headers,
                            verify=False)

    def get_all_scans_by_org_id(self, org_id):
        return requests.get(f'{self.url}/organizations/{org_id}/dasts/',
                            headers=self.headers,
                            verify=False)

    def get_scan_info(self, scan_id):
        return requests.get(f'{self.url}/dasts/{scan_id}/',
                            headers=self.headers,
                            verify=False)

    def get_architectures(self):
        return requests.get(f'{self.url}/architectures/',
                            headers=self.headers,
                            verify=False)

    def get_architecture_types(self):
        return requests.get(f'{self.url}/architecture_types/',
                            headers=self.headers,
                            verify=False)

    def get_testcases(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/testcases/',
                            headers=self.headers,
                            verify=False)

    def get_testcases_for_project(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/testcases/',
                            headers=self.headers,
                            verify=False)

    def create_testcase(self, project_id, testcase_info, app_id, arch_id):
        data = {
            'name': testcase_info['name'],
            'description': testcase_info['description'],
            'application_id': app_id,
            'architecture_id': arch_id
        }
        return requests.post(f'{self.url}/projects/{project_id}/testcases/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def get_testcase(self, testcase_id):
        return requests.get(f'{self.url}/testcases/{testcase_id}/',
                            headers=self.headers,
                            verify=False)

    def start_testcase(self, testcase_id):
        return requests.post(f'{self.url}/testcases/{testcase_id}/start/',
                             headers=self.headers,
                             verify=False)

    def stop_testcase(self, testcase_id):
        return requests.post(f'{self.url}/testcases/{testcase_id}/stop/',
                             headers=self.headers,
                             verify=False)

    def delete_testcase(self, testcase_id):
        return requests.delete(f'{self.url}/testcases/{testcase_id}/',
                               headers=self.headers,
                               verify=False)

    def upload_application(self, path, architecture_type):
        headers_multipart = {'Authorization': self.headers['Authorization']}
        multipart_form_data = {
            'file': (os.path.split(path)[-1], open(path, 'rb'))
        }
        return requests.post(f'{self.url}/organizations/{self.current_context["company"]}/applications/',
                             headers=headers_multipart,
                             files=multipart_form_data,
                             data={'architecture_type': architecture_type},
                             verify=False)

    def create_manual_scan(self, profile_id, app_id, arch_id):
        data = {
            'profile_id': profile_id,
            'application_id': app_id,
            'architecture_id': arch_id,
            'type': 0
        }
        return requests.post(f'{self.url}/organizations/{self.current_context["company"]}/dasts/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def create_auto_scan(self, profile_id, app_id, arch_id, test_case_id):
        data = {
            'profile_id': profile_id,
            'application_id': app_id,
            'architecture_id': arch_id,
            'test_case_id': test_case_id,
            'type': 1
        }
        return requests.post(f'{self.url}/organizations/{self.current_context["company"]}/dasts/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def start_scan(self, dast_id):
        """
        Start automated scan through REST API
        :return: scan info resp(dict)
        """
        return requests.post(f'{self.url}/dasts/{dast_id}/start/',
                             headers=self.headers,
                             verify=False)

    def stop_scan(self, scan_id):
        """
        Get scan status from current scan Id
        :param scan_id: Scan ID to get status
        :return:
        """
        return requests.post(f'{self.url}/dasts/{scan_id}/stop/',
                             headers=self.headers,
                             verify=False)

    def get_scan_issues(self, scan_id):
        return requests.get(f'{self.url}/dasts/{scan_id}/issues/',
                            headers=self.headers,
                            verify=False)

    def get_engines(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/engines/',
                            headers=self.headers,
                            verify=False)

    def get_organizations(self):
        return requests.get(f'{self.url}/organizations/',
                            headers=self.headers,
                            verify=False)

    def get_organization(self, organization_id):
        return requests.get(f'{self.url}/organizations/{organization_id}/',
                            headers=self.headers,
                            verify=False)

    def create_organization(self, org_info):
        data = {
            'name': org_info['name'],
            'description': org_info['description']
        }
        return requests.post(f'{self.url}/organizations/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def update_organization(self, org_info, org_id):
        data = {
            'name': org_info['name'],
            'description': org_info['description']
        }
        return requests.patch(f'{self.url}/organizations/{org_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def delete_organization(self, org_id):
        return requests.delete(f'{self.url}/organizations/{org_id}/',
                               headers=self.headers,
                               verify=False)

    def get_project_rules(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/rules/',
                            headers=self.headers,
                            verify=False)

    def get_project_rule_expressions(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/rule_expressions/',
                            headers=self.headers,
                            verify=False)

    def get_project_rule_modules(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/rule_modules/',
                            headers=self.headers,
                            verify=False)

    def get_organization_rules(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/rules/',
                            headers=self.headers,
                            verify=False)

    def get_organization_rules_by_id(self, org_id):
        return requests.get(f'{self.url}/organizations/{org_id}/rules/',
                            headers=self.headers,
                            verify=False)

    def get_organization_rule_expressions(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/rule_expressions/',
                            headers=self.headers,
                            verify=False)

    def get_organization_rule_modules(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/rule_modules/',
                            headers=self.headers,
                            verify=False)

    def get_organization_injections(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/injections',
                            headers=self.headers,
                            verify=False)

    def get_project_injections(self, project_id):
        return requests.get(f'{self.url}/projects/{project_id}/injections',
                            headers=self.headers,
                            verify=False)

    def get_requirement_groups(self):
        return requests.get(f'{self.url}/requirement_groups/',
                            headers=self.headers,
                            verify=False)

    def get_organization_requirements_groups(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/requirement_groups/',
                            headers=self.headers,
                            verify=False)

    def get_profile_requirements_groups(self, profile_id):
        return requests.get(f'{self.url}/profiles/{profile_id}/requirement_groups/',
                            headers=self.headers,
                            verify=False)

    def get_ci_token(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/ci_token/info',
                            headers=self.headers,
                            verify=False)

    def renew_token(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/ci_token/renew',
                            headers=self.headers,
                            verify=False)

    def replace_token(self):
        return requests.get(f'{self.url}/organizations/{self.current_context["company"]}/ci_token/replace',
                            headers=self.headers,
                            verify=False)

    def get_rules(self):
        return requests.get(f'{self.url}/rules/',
                            headers=self.headers,
                            verify=False)

    def get_settings(self):
        return requests.get(f'{self.url}/settings/',
                            headers=self.headers,
                            verify=False)

    def change_password(self, old_pass, new_pass):
        data = {
            'password': old_pass,
            'new_password': new_pass
        }
        return requests.put(f'{self.url}/currentuser/change_password/',
                            headers=self.headers,
                            data=json.dumps(data),
                            verify=False)

    def change_password_by_admin(self, admin_password, new_user_password, user_id):
        data = {
            'password': admin_password,
            'new_password': new_user_password
        }
        return requests.put(f'{self.url}/users/{user_id}/change_password/',
                            headers=self.headers,
                            data=json.dumps(data),
                            verify=False)

    def add_rule_to_organization(self, org_id, rule_data, is_used):
        data = {
            'is_used': is_used,
            'name': rule_data['name'],
            'description': rule_data['description']
        }
        return requests.post(f'{self.url}/organizations/{org_id}/rules/',
                             headers=self.headers,
                             data=json.dumps(data),
                             verify=False)

    def change_rule(self, rule_id, new_rule_data):
        data = {
            'name': new_rule_data['name'],
            'description': new_rule_data['description']
        }
        return requests.patch(f'{self.url}/rules/{rule_id}/',
                              headers=self.headers,
                              data=json.dumps(data),
                              verify=False)

    def delete_rule(self, rule_id):
        return requests.delete(f'{self.url}/rules/{rule_id}/',
                               headers=self.headers,
                               verify=False)

    def download_report(self, dast_id):
        report = requests.get(f'{self.url}/dasts/{dast_id}/report/',
                              allow_redirects=True,
                              headers=self.headers,
                              verify=False)
        return report

    def get_dast_logs(self, dast_id):
        return requests.get(f'{self.url}/dasts/{dast_id}/log/',
                            headers=self.headers,
                            verify=False)

    def download_dast_logs(self, dast_id):
        logs = requests.get(f'{self.url}/dasts/{dast_id}/log/download/',
                            allow_redirects=True,
                            headers=self.headers,
                            verify=False)
        return logs

    def get_testcase_logs(self, testcase_id):
        return requests.get(f'{self.url}/testcases/{testcase_id}/log/',
                            headers=self.headers,
                            verify=False)

    def download_testcase_logs(self, testcase_id):
        logs = requests.get(f'{self.url}/testcases/{testcase_id}/log/download/',
                            allow_redirects=True,
                            headers=self.headers,
                            verify=False)
        return logs
