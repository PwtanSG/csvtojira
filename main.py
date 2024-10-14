# This is a sample Python script to load QA records in csv and
# perform create/update to the records in Jira Project.

import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import os
from dotenv import load_dotenv
import jira_module
import pandas as pd


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


def qa_file_get_df():
    df = pd.read_csv(qa_filename)
    if df.empty:
        print('No data in ' + qa_filename)
        exit(1)

    print(df.to_string())
    for ind in df.index:
        print(df['QN no.'][ind], df['Title'][ind])

    return df


def jira_qn_no_list(issues_list):
    qn_no_list = []
    for issue in issues_list:
        if issue['fields']['customfield_10042']:
            qn_no_list.append(issue['fields']['customfield_10042'])
    return qn_no_list


def jira_qn_dict_list(issues_list):
    qn_dict_list = []
    for issue in issues_list:
        if issue['fields']['customfield_10042']:
            qn_dict = {'key': issue['key'], 'QN no.': issue['fields']['customfield_10042']}
            qn_dict_list.append(qn_dict)
    return qn_dict_list


def is_qn_no_in_jira(qn_no, jira_qn_dict_list_):
    res_list = [item for item in jira_qn_dict_list_ if item['QN no.'] == qn_no]
    if len(res_list) == 1:
        return {'result': True, 'record': res_list[0]}
    else:
        return {'result': False, 'record': []}


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Start script...')
    # jira_module.get_jira_project_info(jira_project_key)
    # jira_module.get_jira_project_info('QI')
    jira_all_issues_list = jira_module.jira_get_all_issues('QI')
    jira_qn_num_list = jira_qn_no_list(jira_all_issues_list)
    jira_qn_dic_list = jira_qn_dict_list(jira_all_issues_list)

    qa_file_df = qa_file_get_df()
    for index, csv_row in qa_file_df.iterrows():
        find_qn = is_qn_no_in_jira(csv_row['QN no.'], jira_qn_dic_list)
        if find_qn['result']:
            # existing QN, edit record in Jira
            jira_module.jira_edit_issue(find_qn['record']['key'], csv_row)
        else:
            # new QN create record in Jira
            jira_module.jira_create_issue(csv_row)
    print('Completed script...')
