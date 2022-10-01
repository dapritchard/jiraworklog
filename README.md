# jiraworklog

jiraworklog is a command line application that synchronizes worklog entries between your local machine and a Jira server. The main functionality that it provides is:
<!-- jiraworklog enables a workflow where you can track your worklogs using your favorite effort tracking system or Excel spreadsheet and then upload the relevant portion of the worklogs to Jira without any manual entry of the worklogs. -->

* Reading your worklogs on your local machine from either a [delimiter-separated values](delimiter-separated values) format such as CSV or an Excel format.
* Tracking any additions, modifications, or deletions of worklogs on your local machine and uploading the appropriate changes to your worklogs on the Jira server.

Once you have a configuration file set up then uploading worklogs to the Jira server is as simple as providing the worklogs to the `jiraworklog` application through standard input or via the `--file` argument.

```
> cat worklogs.csv
description,start,end,tags
Data pipeline,2021-01-12 10:00,2021-01-12 10:30,p1
Write specifications,2021-01-12 13:15,2021-01-12 14:15,p1
Add routines,2021-01-12 15:45,2021-01-12 17:00,p2

> jiraworklog --file worklogs.csv

Auto-confirm. The following changes will be made.

-- Add to remote worklogs ----------------------------------
Tuesday January 12, 2021
    P9992-3    10:00-10:30    (0:30)    Data pipeline
    P9992-3    13:15-14:15    (1:00)    Write specifications
```


## Installation

jiraworklog is a Python application and is distributed through PyPI.
If you have Python available on your machine then you can install it with a command like the following.

```
python -m pip install jiraworklog --user
```


## Basic usage

TODO


## Supported worklog formats

Currently delimiter-separated values formats such as CSV or Excel format is supported.


## Configuration setup

TODO

### Jira authentication

TODO
