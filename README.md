# jiraworklog

jiraworklog is a command line application that synchronizes worklog entries between your local machine and a Jira server. The main functionality that it provides is:
<!-- jiraworklog enables a workflow where you can track your worklogs using your favorite effort tracking system or Excel spreadsheet and then upload the relevant portion of the worklogs to Jira without any manual entry of the worklogs. -->

* Reading your worklogs on your local machine from either a [delimiter-separated values](https://en.wikipedia.org/wiki/Delimiter-separated_values) format such as CSV or an Excel format.
* Tracking any additions, modifications, or deletions of worklogs on your local machine and uploading the appropriate changes to your worklogs on the Jira server.

Once you have a configuration file set up then uploading worklogs to the Jira server is as simple as providing the worklogs to the `jiraworklog` application through standard input or via the `--file` argument.

```
> cat worklogs.csv
description,start,end,tags
Data pipeline,2021-01-12 10:00,2021-01-12 10:30,P9992-3
Write specifications,2021-01-12 13:15,2021-01-12 14:15,P9992-3

> jiraworklog --file worklogs.csv

Auto-confirm. The following changes will be made.

-- Add to remote worklogs ----------------------------------
Tuesday January 12, 2021
    P9992-3    10:00-10:30    (0:30)    Data pipeline
    P9992-3    13:15-14:15    (1:00)    Write specifications
```


## Installation

jiraworklog is a Python application and is distributed through PyPI.
If you have Python 3.9 or greater available on your machine then you can install it with a command like the following.

```
python -m pip install jiraworklog --user
```


## Basic usage

### Overview

 <!-- See the [Configuration file setup](#configuration-file-setup) Section for further details on this step. -->
jiraworklog requires a configuration file to be set up providing information about how to parse local worklog entries and Jira server authentication, among other things. Once the configuration file has been set up, provide your worklogs to the `jiraworklog` application either through standard input or via the `--file` argument. The application determines whether there have been any additions, modifications, or deletions of worklogs on your local machine and uploads the appropriate changes to your worklogs on the Jira server. When all of the worklogs that appear in the Jira server have been uploaded via jiraworklog, this amounts to synchronizing the worklogs from your local worklogs with the Jira server.

The other ways that worklogs can appear on the Jira server are through the Jira web application or web API. When worklogs are placed on the Jira server that jiraworklog isn't aware of, it effectively ignores those worklogs with the one exception that if an identical worklog is added to the local worklogs then it is considered to correspond to the appropriate remote worklog. This policy prevents jiraworklog from uploading the worklog a second time and also links the local and remote worklogs so that a future change in the local worklog results in a corresponding change to the remote worklog.


### Viewing the available command-line options

Use the `--help` option to view the available command-line options.
```
jiraworklog --help
```


### Reading in worklogs

If the local worklogs are stored in a file `worklogs.csv` then you can use a command like the following to upload your worklogs to the Jira server.
```
jiraworklog --file worklogs.csv
```

Similarly you can pass the local worklogs in via standard input.
```
cat worklogs.csv | jiraworklog
```

If you have an Excel file then you can also read it in using the `--file` option. Reading Excel files from standard input is currently not supported.
```
jiraworklog --file worklogs.xlsx
```


## Jira authentication

<!-- https://developer.atlassian.com/server/jira/platform/rest-apis/#authentication-and-authorization -->
<!-- https://developer.atlassian.com/server/jira/platform/basic-authentication/ -->
Jira supports two forms of authentication for it's API: basic authentication and OAuth. Currently only basic authentication is supported by jiraworklog.

Authentication to Jira via basic authentication requires the use of an API token. You can create a token if you do not have one by following the instructions found in the [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) page in the Atlassian Support website.


## Configuration file setup

jiraworklog requires a configuration file to be set up providing information about how to parse local worklog entries and Jira server authentication, among other things. The configuration file setup is the most complicated part of getting jiraworklog up and running, but once it is set up you will usually not need to touch it except to specify new Jira issues.

You can see the full configuration file specification in [Configuration file format](#configuration-file-format). But usually the easiest way to create a new configuration file is by using the `--init` command-line option as shown in the following example. This will run an interactive script that prompts your for the necessary information and then constructs a configuration file for you using that information.


### Configuration file location

By default the `jiraworklog` application looks for the configuration file at `~/.jwconfig.yaml`. If your configuration file is in a different location then you can specify it by using the `--config-path` command-line option as shown in the following example.
```
jiraworklog --init
```


### Configuration file format

The jiraworklog configuration file is required to follow a YAML format.


## Related software

TODO
