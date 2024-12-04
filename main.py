# This is a sample Python script to load QA records in csv and
# perform create/update to the records in Jira Project.

from JiraManager import *
import sys

load_dotenv()
jira_cloud_id = os.getenv('JIRA_CLOUD_ID')
jira_cloud_api_endpoint = os.getenv('JIRA_CLOUD_API_ENDPOINT')
jira_user = os.getenv('JIRA_USER')
jira_api_token = os.getenv('JIRA_API_TOKEN')
jira_project_key = os.getenv('JIRA_PROJECT_KEY')
auth = HTTPBasicAuth(jira_user, jira_api_token)
jira_cloud_api_baseurl = f'{jira_cloud_api_endpoint}{jira_cloud_id}/rest/api/3'
jira_project_info = ''
qa_file_ext = 'csv'
qa_file_dir = 'csv'
qa_filename = 'QA_20241012.csv'
qa_file_df = ''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print('Start script...')
    qa_filename = Utility.get_cmd_main_fn_arg(qa_filename, sys.argv)
    edit_count = 0
    create_count = 0
    jira_manager = JiraManager()

    qa_file_df = Utility.read_qa_csvfile_get_df(f"{qa_file_dir}/{qa_filename}")
    print(f"{qa_filename} : {len(qa_file_df)} records")
    jira_issues_list = jira_manager.jira_get_all_issues(jira_project_key)

    for index, csv_row in qa_file_df.iterrows():
        qn_no_in_jira = Utility.find_qn_in_jira(jira_issues_list, csv_row['QN no.'])
        if qn_no_in_jira['result']:
            # existing QN, edit record in Jira
            no_diff = Utility.compare_data_row_csv_jira(csv_row, qn_no_in_jira['record'])
            if not no_diff:
                res = jira_manager.jira_edit_issue(qn_no_in_jira['record'].key, csv_row)
                if res['result']:
                    edit_count += 1
        else:
            # new QN create record in Jira
            res = jira_manager.jira_create_issue(csv_row)
            if res['result']:
                create_count += 1

    print(f'Completed script... CSV records: {len(qa_file_df)} Edited: {edit_count} Created: {create_count}')
