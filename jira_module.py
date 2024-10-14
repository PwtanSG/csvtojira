# This is a sample Python script to load QA records in csv and
# perform create/update to the records in Jira Project.

import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import os
from dotenv import load_dotenv

load_dotenv()
jira_cloud_id = os.getenv('JIRA_CLOUD_ID')
jira_cloud_api_endpoint = os.getenv('JIRA_CLOUD_API_ENDPOINT')
jira_user = os.getenv('JIRA_USER')
jira_api_token = os.getenv('JIRA_API_TOKEN')
jira_project_key = os.getenv('JIRA_PROJECT_KEY')
auth = HTTPBasicAuth(jira_user, jira_api_token)
jira_cloud_api_baseurl = f'{jira_cloud_api_endpoint}{jira_cloud_id}/rest/api/3'
jira_project_info = ''


def check_response(func_name, response):
    if response.status_code >= 400:
        print(f'{func_name} - status code : {response.status_code}')
        if response.text:
            try:
                data = json.loads(response.text)
                if isinstance(data, dict):
                    for key in data:
                        print(f'{key} : {data[key]}')
                else:
                    print(response.text)
                # print(data['errorMessages'], f'Error: {response.status_code}{response.text}')['errorMessage' in data]
            except:
                print(f'Error: {response.status_code}')
        exit(1)
    return


def get_jira_project_info(project_key):
    url = f'{jira_cloud_api_baseurl}/project/{project_key}'

    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    check_response(get_jira_project_info.__name__, response)
    global jira_project_info
    jira_project_info = json.loads(response.text)
    print(jira_project_info)
    # print(data)


def jiraBoard():
    url = f'{jira_cloud_api_baseurl}/search'
    # print(url)
    # auth = HTTPBasicAuth(jira_user, jira_access_token)

    headers = {
        "Accept": "application/json"
    }

    query = {
        'jql': 'project = ' + jira_project_key
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query,
        auth=auth
    )

    data = json.loads(response.text)
    selectedIssues = []
    print(data['total'])
    # Get all issues and put them into an array
    # for issue in data['issues']:
    #     print(issue)
    #     selectedIssues.append(issue)

    # Save data from Jira into a csv file
    # with open('issues.csv', 'w', newline='') as csvfile:
    #     fieldnames = ['expand', 'key', 'id', 'fields', 'self']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     for issue in selectedIssues:
    #         writer.writerow(issue)


def jira_get_all_issues(project_key):
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

    data = json.loads(response.text)
    selectedIssues = []

    print(data['total'])
    # Get all issues and put them into an array
    for issue in data['issues']:
        # print(issue)
        selectedIssues.append(issue)
    print(selectedIssues)

    return data['issues']

    # Save data from Jira into a csv file
    # with open('issues.csv', 'w', newline='') as csvfile:
    #     fieldnames = ['expand', 'key', 'id', 'fields', 'self']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     for issue in selectedIssues:
    #         writer.writerow(issue)


def jira_get_issue():
    url = f'{jira_cloud_api_baseurl}/issue/QI-1'
    print(url)
    # auth = HTTPBasicAuth(jira_user, jira_access_token)

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

    data = json.loads(response.text)
    print(data)


def jira_edit_issue(jira_issue_key, df_row):
    url = f'{jira_cloud_api_baseurl}/issue/' + jira_issue_key
    # print(url)
    # auth = HTTPBasicAuth(jira_user, jira_access_token)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # query = {
    #     'jql': 'project = FAS'
    # }

    # payload = json.dumps({
    #     "fields": {
    #         # "customfield_10042": "QN0013141",  # custom field for reference no.
    #         "summary": "Completed orders still displaying in pending"
    #     }
    # })

    payload = json.dumps({
        "fields": {
            "summary": df_row['Title'],
            # "customfield_10042": df_row['QN no.'],
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
        "PUT",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    # data = json.loads(response.text)
    # print(response)
    print(response)
    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))


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
            "customfield_10042": df_row['QN no.'],
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
    print(response)
