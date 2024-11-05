import json
import pandas as pd


def qa_file_get_df(qa_filename):
    df = pd.read_csv(qa_filename)
    if df.empty:
        print('No data in ' + qa_filename)
        exit(1)

    duplicated_qn_no = df['QN no.'].duplicated()
    dup_result_bool_list = duplicated_qn_no.tolist()
    if True in dup_result_bool_list:
        ind = dup_result_bool_list.index(True)
        print(f"Abort : Duplicated QN no. found in {qa_filename} : {df['QN no.'][ind]}")
        exit(1)

    # for ind in df.index:
    #     print(df['QN no.'][ind], df['Title'][ind])

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


def find_qn_in_jira(jira_issues_list, csv_row_qn_no):

    result_list = [jira_issue for jira_issue in jira_issues_list if jira_issue.qn_no == csv_row_qn_no]
    if len(result_list) == 1:
        return {'result': True, 'record': result_list[0]}
    else:
        return {'result': False, 'record': []}
