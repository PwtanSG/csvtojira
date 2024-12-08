import json
import logging
from datetime import datetime

import pandas as pd
import pathlib
import numpy as np

from JiraIssue import JiraIssue

required_cols = ['QN no.', 'Title', 'Description']


def check_file_exist(qa_file_pathname_, logger_):
    if qa_file_pathname_:
        filepath = pathlib.Path(qa_file_pathname_)
        if filepath.exists():
            # print(filepath)
            return filepath.exists()
        else:
            logger_.error(f"Abort : File path/name not found - {qa_file_pathname_}")
            exit(1)
    else:
        logger_.error(f"Abort : File path/name not provided")
        exit(1)


def check_column_value_empty(dataframe, column_name, logger_):
    result = dataframe[column_name].isnull().any()
    if result:
        logger_.error(f'{column_name} column : Null data detected.')
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


def validate_qn_no_column(df_, column_to_validate, logger_):
    """
    validate QN no. format - 9 char long, prefix with 'QN' and 7 digit (e.g QN1234567)
    :param df_:
    :param column_to_validate:
    :return:none
    """
    pattern = r"^[Qq][Nn][0-9]{7}$"
    # invalid_values = df_[column_to_validate][~df_[column_to_validate].astype(str).str.match(pattern, na=False)]
    invalid_values = df_[column_to_validate].str.match(pattern)
    invalid_values_ndarray = invalid_values.values
    invalid_found = np.where(invalid_values_ndarray == False)[0]
    if invalid_found.size:
        abort_msg = f'Abort : invalid QN no. found : '
        for i in range(invalid_found.size):
            abort_msg += df_[column_to_validate][i] + ' '
        logger_.error(abort_msg)
        exit(1)

    # enumerate method
    # invalid_values_list = invalid_values_ndarray.tolist()
    # invalid_values_indices = [index for (index, item) in enumerate(invalid_values_list) if not item]
    # if len(invalid_values_indices):
    #     for i in range(len(invalid_values_indices)):
    #         print(f'invalid QN no. found: {df_[column_to_validate][i]}')


def read_qa_csvfile_get_df(qa_filename_, logger_):
    logger_.info(f"Reading file : {qa_filename_}")
    check_file_exist(qa_filename_, logger_)

    df = pd.read_csv(qa_filename_, usecols=required_cols)
    if df.empty:
        logger_.warning('No data in ' + qa_filename_)
        exit(1)

    logger_.info(f"{qa_filename_} : {str(len(df))} records")

    check_column_value_empty(df, required_cols[0], logger_)

    no_dup_qn_no = check_no_duplicated_qn_no(qa_filename_, df)
    if not no_dup_qn_no['result']:
        logger_.warning(no_dup_qn_no['result'])
        logger_.warning(no_dup_qn_no['msg'])
        exit(1)

    validate_qn_no_column(df, required_cols[0], logger_)

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


def check_response(func_name, response, logger_):
    # print(f'{func_name} - status code : {response.status_code} {response.text}')
    if response.status_code >= 400:
        logger_.info(f'{func_name} - status code : {response.status_code}')
        if response.text:
            try:
                data = json.loads(response.text)
                if isinstance(data, dict):
                    for key in data:
                        if key != 'JIRA_CLOUD_ID':
                            logger_.info(f'{key} : {data[key]}')
                else:
                    logger_.info(response.text)
                # print(data['errorMessages'], f'Error: {response.status_code}{response.text}')['errorMessage' in data]
            except:
                logger_.error(f'Error: {response.status_code}')
        return {"result": False, "status_code": response.status_code}
    return {"result": True, "status_code": response.status_code}


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


def get_cmd_main_fn_arg(default_fn, argv):
    """
    :param default_fn:
    :param argv: execute main.py in cmd with filename argument pass in from cmd
    :return: str - if found csv filename pass via argument else use default_fn
    """
    rtn_fn = default_fn
    n = len(argv)
    if n > 1 and argv[0] == "main.py":
        arg1 = argv[1]
        if arg1.endswith("csv"):
            rtn_fn = arg1
    return rtn_fn


def init_logging():

    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : [%(filename)s:%(lineno)s - %(funcName)s()] : %(message)s",
        "%Y-%m-%d %H:%M:%S")
    logfile_path = "log/" + datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".log"

    # create log object
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    # create log file handler
    fh = logging.FileHandler(f"{logfile_path}", mode='w', encoding='utf-8')
    # fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler
    ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info(f"Init logger : log file - {logfile_path}")

    return logger
