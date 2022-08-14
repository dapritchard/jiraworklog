# jiraworklog

jiraworklog synchronizes worklog entries between your local machine and a Jira server. The main functionality that it provides is:

* Reading your worklogs on your local machine from one of a number of supported formats such as CSV (this is currently the only supported format).
* Figuring out which worklogs need to be added or removed from the Jira server. This means that:
    * You don't have to keep track of which worklogs you need to submit and can submit the entirety of your records each time to jiraworklog.
    * You can modify or remove existing worklogs and those changes will be properly reflected.
* Performing the appropriate changes on the Jira server.


## Installation

Currently, you have to fork the project. The goal is to have a beta release on PyPI.


## Supported formats

Currently only the CSV file format is supported. The goal is to add support for other similar delimited file formats as well as for Excel.
