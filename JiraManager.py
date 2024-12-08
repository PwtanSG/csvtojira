import json
import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import Utility
from JiraIssue import *

load_dotenv()
jira_cloud_id = os.getenv('JIRA_CLOUD_ID')
jira_cloud_api_endpoint = os.getenv('JIRA_CLOUD_API_ENDPOINT')
jira_user = os.getenv('JIRA_USER')
jira_api_token = os.getenv('JIRA_API_TOKEN')
jira_project_key = os.getenv('JIRA_PROJECT_KEY')
jira_custom_field_qn_no = os.getenv('JIRA_CUSTOM_FIELD_QN_NO')
auth = HTTPBasicAuth(jira_user, jira_api_token)
jira_cloud_api_baseurl = f'{jira_cloud_api_endpoint}{jira_cloud_id}/rest/api/3'
jira_project_info = ''


class JiraManager:
    def __init__(self):
        self.issues = []

    def get_class_name(self):
        return self.__class__.__name__

    def jira_get_all_issues(self, project_key, logger_):

        url = f'{jira_cloud_api_baseurl}/search'

        headers = {
            "Accept": "application/json"
        }

        query = {
            'jql': 'project =' + project_key
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query,
            auth=auth
        )
        res = Utility.check_response('jira_get_all_issues', response, logger_)
        if not res['result']:
            exit(1)
        data = json.loads(response.text)

        for issue in data['issues']:
            self.issues.append(JiraIssue(issue['key'], issue['fields']['summary'],
                                         issue['fields'][jira_custom_field_qn_no],
                                         issue['fields']['description']))
        return self.issues

    def jira_get_issue(self, issue_key):
        print(f'get {issue_key}')
        if not issue_key or 'QI-' not in issue_key:
            print(f'Error issue key {issue_key}')
            return False

        url = f'{jira_cloud_api_baseurl}/issue/{issue_key}'

        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            # params=query,
            auth=auth
        )

        # Utility.check_response(self.get_class_name(), response)
        Utility.check_response(self.jira_get_issue.__name__, response)
        issue = json.loads(response.text)

        return JiraIssue(issue['key'], issue['fields']['summary'], issue['fields'][jira_custom_field_qn_no],
                         issue['fields']['description'])

    @staticmethod
    def jira_edit_issue(jira_issue_key, df_row):
        url = f'{jira_cloud_api_baseurl}/issue/' + jira_issue_key

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps({
            "fields": {
                "summary": df_row['Title'],
                # jira_custom_field_qn_no : df_row['QN no.'], # not allow to update QN_NO
                "description": {
                    "type": "doc",  # required
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": df_row['Description']
                                }
                            ]
                        }
                    ]
                },
            }
        })

        response = requests.request(
            "PUT",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )

        # data = json.loads(response.text)
        # print(response)
        res = Utility.check_response("jira_edit_issue", response)
        msg_ = f"Edit {jira_issue_key} : {res['status_code']}"
        print(msg_ + " - successful.") if res['result'] else print(msg_ + "unsuccessful.")
        return res

    @staticmethod
    def jira_create_issue(df_row):

        url = f'{jira_cloud_api_baseurl}/issue'
        # print(url)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps({
            "fields": {
                "issuetype": {
                    "id": "10019"
                },
                "project": {
                    "id": "10007"
                },
                "summary": df_row['Title'],
                jira_custom_field_qn_no: df_row['QN no.'],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": df_row['Description']
                                }
                            ]
                        }
                    ]
                },
            }
        })

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )

        # data = json.loads(response.text)
        # print(response)
        res = Utility.check_response("jira_create_issue", response)
        msg_ = f"Create {df_row['QN no.']} : {res['status_code']}"
        print(msg_ + " - successful.") if res['result'] else print(msg_ + "unsuccessful.")
        return res
