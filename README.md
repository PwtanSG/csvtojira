# Introduction
Jira has a import csv function but at that point in time, this import features was not able to automate it as batch job to daily upload new records in csv into Jira without human intervention.

The CSV to Jira Quality Issue Project demonstrates the implementation of JIRA Cloud REST API in Python to create/update JIRA issues based on the 
list of Quality Issue records in CSV file in a python script and to be run daily as a cron batch job.

## JiraIssue
The JiraIssue class represents an individual Jira Issue with the following attributes:

key: The key of the Quality Issue. \
summary: The age of the Quality Issue. \
description: The description of the Quality Issue. \
qn_no: Quality Issue notification number (using Jira Customed field) \
[QN no. format - 9 char long, prefix with 'QN' and 7 digit (e.g QN1234567)]

## JiraManager
The JiraManager class is responsible for managing a list of employees. It offers functionalities to:

#### - Add a new Quality Issue to JIRA project. 
#### - List all existing Quality Issues in JIRA project.
#### - Update an Quality Issue details by Issue key.
QN_no is unique to the Quality Issue reported hence it cannot be updated.
Only Title and description field can be update based on the content in csv file.
#### - Find a Quality Issue by Quality Issue notification no.(QN_No.). 

## Utility
Utility.read_qa_csvfile_get_df
- any duplication/blank of QN no.(quality tracking number) in CSV (as QN is unique tracking no.)
- QN no. format - 9 char long, prefix with 'QN' and 7 digit (e.g QN1234567)

## Setup
### environment variable
Create Environment variables as follows and saved as .env file. Refer to .env_example.
JIRA_PROJECT_KEY=
JIRA_USER=
JIRA_API_TOKEN=
JIRA_CLOUD_ID=
JIRA_CLOUD_API_ENDPOINT=
JIRA_CUSTOM_FIELD_QN_NO=

### CSV file location: 
./csv

### script usage
CMD - takes 1 arg of csv filename
py main.py filename.csv

### reference 
JIRA REST API https://docs.atlassian.com/software/jira/docs/api/REST/1000.824.0/    \
JIRA API TOKEN https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/   \
Python logging https://docs.python.org/3/library/logging.html#logging.Logger \
