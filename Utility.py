import json
import pandas as pd
import pathlib
import numpy as np

from JiraIssue import JiraIssue

required_cols = ['QN no.', 'Title', 'Description']


def check_file_exist(qa_file_pathname):
    if qa_file_pathname:
        filepath = pathlib.Path(qa_file_pathname)
        if filepath.exists():
            print(filepath)
            return filepath.exists()
        else:
            print(f"Abort : File path/name not found - {qa_file_pathname}")
            exit(1)
    else:
        print(f"Abort : File path/name not provided")
        exit(1)


def check_column_value_empty(dataframe, column_name):
    result = dataframe[column_name].isnull().any()
    if result:
        print(f'{column_name} column : Null data detected.')
    return result


def check_no_duplicated_qn_no(qa_file_pathname, qa_file_df):
    """
    :param qa_file_pathname:
    :param qa_file_df:
    :return:
        True if NO duplicated QN no.
        False if duplicated QN no. EXIST. msg text showing the duplicated QN no.
    """

    msg_ = f"Abort : Duplicated QN no. found in {qa_file_pathname} : "
    duplicated_qn_no = qa_file_df['QN no.'].duplicated()
    dup_result_bool_list = duplicated_qn_no.tolist()
    res = {"result": True, "msg": ''}
    for item in dup_result_bool_list:
        if item:
            ind = dup_result_bool_list.index(True)
            msg_ = msg_ + qa_file_df['QN no.'][ind] + ' '
            res = {"result": False, "msg": msg_}
    return res


def validate_qn_no_column(df_, column_to_validate):
    pattern = r"^[Qq][Nn][0-9]{7}$"
    # invalid_values = df_[column_to_validate][~df_[column_to_validate].astype(str).str.match(pattern, na=False)]
    invalid_values = df_[column_to_validate].str.match(pattern)
    invalid_values_ndarray = invalid_values.values
    invalid_found = np.where(invalid_values_ndarray == False)[0]
    if invalid_found.size:
        abort_msg = f'Abort : invalid QN no. found : '
        for i in range(invalid_found.size):
            abort_msg += df_[column_to_validate][i] + ' '
        print(abort_msg)
        exit(1)

    # enumerate method
    # invalid_values_list = invalid_values_ndarray.tolist()
    # invalid_values_indices = [index for (index, item) in enumerate(invalid_values_list) if not item]
    # if len(invalid_values_indices):
    #     for i in range(len(invalid_values_indices)):
    #         print(f'invalid QN no. found: {df_[column_to_validate][i]}')


def read_qa_csvfile_get_df(qa_filename):
    check_file_exist(qa_filename)

    df = pd.read_csv(qa_filename, usecols=required_cols)
    if df.empty:
        print('No data in ' + qa_filename)
        exit(1)

    check_column_value_empty(df, required_cols[0])

    no_dup_qn_no = check_no_duplicated_qn_no(qa_filename, df)
    if not no_dup_qn_no['result']:
        print(no_dup_qn_no['result'])
        print(no_dup_qn_no['msg'])
        exit(1)

    validate_qn_no_column(df, required_cols[0])

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


def compare_data_row_csv_jira(csv_row_, jira_issue_):
    """
    This compare a single csv record with the corresponding jira project issue of following fields
    qn_no, title=summary, description
    :param csv_row_: pandas series - row records in csv file
    :param jira_issue_: class datatype JiraIssue - issue from jira record
    :return: True if no changes
    """
    jira_issue_desc_text = jira_issue_.description['content'][0]['content'][0]['text']
    return jira_issue_.qn_no == csv_row_[required_cols[0]] and jira_issue_.summary == csv_row_['Title'] \
        and jira_issue_desc_text == csv_row_['Description']

