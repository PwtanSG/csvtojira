# This is a sample Python script to load QA records in csv and
# perform create/update to the records in Jira Project.

import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import os
from dotenv import load_dotenv
import Utility
import jira_module
import pandas as pd
from JiraManager import *

load_dotenv()
jira_cloud_id = os.getenv('JIRA_CLOUD_ID')
jira_cloud_api_endpoint = os.getenv('JIRA_CLOUD_API_ENDPOINT')
jira_user = os.getenv('JIRA_USER')
jira_api_token = os.getenv('JIRA_API_TOKEN')
jira_project_key = os.getenv('JIRA_PROJECT_KEY')
auth = HTTPBasicAuth(jira_user, jira_api_token)
jira_cloud_api_baseurl = f'{jira_cloud_api_endpoint}{jira_cloud_id}/rest/api/3'
jira_project_info = ''
qa_filename = 'QA_20241012.csv'
qa_file_df = ''


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Start script...')
    jira_manager = JiraManager()

    qa_file_df = Utility.qa_file_get_df(qa_filename)
    # jira_manager.jira_get_issue('QI-12')
    jira_issues_list = jira_manager.jira_get_all_issues(jira_project_key)

    for index, csv_row in qa_file_df.iterrows():
        qn_no_in_jira = Utility.find_qn_in_jira(jira_issues_list, csv_row['QN no.'])
        if qn_no_in_jira['result']:
            # existing QN, edit record in Jira
            jira_manager.jira_edit_issue(qn_no_in_jira['record'].key, csv_row)

        else:
            # new QN create record in Jira
            jira_manager.jira_create_issue(csv_row)

    # print(issue.key)
    # print(issue.__dict__)
    # items = issue.__dict__.items()
    # if items:
    #     [print(f"key: {k}    value: {v}") for k, v in items]
    print('Completed script...')
    # app = JiraManager.list_jira_issues('QI')
    # app.run()
