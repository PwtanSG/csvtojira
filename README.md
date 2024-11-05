# Introduction
The CSV to Jira Quality Issue Project demonstrates the implementation of JIRA Cloud REST API in Python to create/update JIRA issues based on the 
list of Quality Issue records in CSV file

## JiraIssue
The JiraIssue class represents an individual Jira Issue with the following attributes:

key: The key of the Quality Issue. \
summary: The age of the Quality Issue. \
description: The description of the Quality Issue. \
qn_no: Quality Issue notification number (using Jira Customed field) 

# JiraManager
The JiraManager class is responsible for managing a list of employees. It offers functionalities to:

Add a new Quality Issue to JIRA project. \
List all existing Quality Issues in JIRA project. \
Update an Quality Issue details by Issue key. \
Find a Quality Issue by Quality Issue notification no.(QN_No.). 


### reference 
JIRA REST API https://docs.atlassian.com/software/jira/docs/api/REST/1000.824.0/