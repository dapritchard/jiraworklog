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

jiraworklog is a Python application distributed through PyPI.
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
```
jiraworklog --init
```


### Configuration file location

By default the `jiraworklog` application looks for the configuration file at `~/.jwconfig.yaml`. If you store your configuration file at that location then you need only provide your worklogs when you invoke the `jiraworklog` application.
```shell
# Assumes that your configuration file is located at ~/.jwconfig.yaml
jiraworklog --file worklogs.csv
```

If your configuration file is not located in the default location then you can specify it by using the `--config-path` command-line option.
```
# If your configuration file is located at e.g. path/to/jwconfig.yaml
jiraworklog --config-path path/to/jwconfig.yaml --file worklogs.csv
```


### Configuration file format

The jiraworklog configuration file is required to follow a YAML format.

An example of a valid configuration file is shown below. We'll break down the various elements in the following sections.
``` yaml
jwconfig_version: 0.1.0

auth_token:
  server: "https://runway.atlassian.net"
  user: "daffy@runway.com"
  api_token: "J6ab6YMa1HVWADNOmO6TC623"

issues_map:
  p1: "P01"
  p2: "P02"

# If you are using an Excel file then this field gets replaced by a
# `parse_excel` stanza
parse_delimited:
  dialect:
    delimiter: ","
  col_labels:
    description: "task"
    start: "start"
    end: "end"
    tags: "tags"
  col_formats:
    start: "%Y-%m-%d %H:%M"
    end: "%Y-%m-%d %H:%M"
  delimiter2: ":"
  timezone: "US/Eastern"
```


#### Configuration file version specification

The configuration file version specification is used so that the `jiraworklog` application knows how to read a given configuration file. An example version specification key value pair is shown below.

``` yaml
jwconfig_version: 0.1.0
```

`jwconfig_version` is a string providing the jiraworklog version for which the configuration file was written.


#### Configuration file authentication specification

Currently the only form of authentication supported by jiraworklog is basic authentication using an API token. An example basic authentication mapping is shown below.

``` yaml
basic_auth:
  server: "https://runway.atlassian.net"
  user: "daffy@runway.com"
  api_token: "J6ab6YMa1HVWADNOmO6TC623"
```

There are three possible keys within the `basic_auth` mapping. If you do not wish to store one or more of these values in the configuration file then you can instead provide a given value by using an environmental variable as described below.

* `server`: a string providing the server URL. If this value is omitted or `null` then `jiraworklog` reads in the information from the `JW_SERVER` environmental variable.
* `user`: a string providing the user ID, which is usually an email address. If this value is omitted or `null` then `jiraworklog` reads in the information from the `JW_USER` environmental variable.
* `api_token`: a string providing a user's API token. See the [Jira authentication](#-jira-authentication) section for details on how to create an API token. If this value is omitted or `null` then `jiraworklog` reads in the information from the `JW_API_TOKEN` environmental variable.


#### Configuration file issues mapping

The issues mapping section of the configuration file specifies a mapping of your local worklog tags to the names of the corresponding Jira issues. The names of the local tags and their corresponding Jira issue keys might be the same, but they need not be. You are also allowed to have multiple local tags map to the same Jira issue (thus your worklogs can be finer-grained than the Jira issues).

In the following example there are 3 mappings from local tags to Jira issues. The first entry maps worklogs tagged with `local-p1-1`to the Jira issue with key `P01`, while the second entry maps worklogs tagged with `local-p1-2` to the same Jira issue with key `P01`. The last entry maps entries tagged with `local-p2`to the Jira issue with key `P02`.

``` yaml
issues_map:
  local-p1-1: "P01"
  local-p1-2: "P01"
  local-p2:   "P02"
```

There are 0 or more key/value pairs in the `issues_map` mapping (although note that there's nothing for jiraworklog to do when there are 0 entries). Each value must be a string corresponding to a Jira issue key, and multiple entries are allowed to correspond to the same Jira issue.


#### Configuration file worklog parsing

The worklog parsing section of the configuration file provides the information for jiraworklog to know how to read in the local worklogs. Currently jiraworklog supports either delimiter-separated values formats such as CSV or an Excel format.

In the event that your worklogs are represented using a delimiter-separated values format such as CSV then you will need to provide a `parse_delimited` section in the configuration file as described in the [Delimiter-separated values worklog parsing](#-delimiter-separated-values-worklog-parsing) section.

In the event that your worklogs are represented using an Excel format then you will need to provide a `parse_excel` section in the configuration file as described in the [Excel worklog parsing](#-excel-worklog-parsing) section.


#### Delimiter-separated values worklog parsing 

If your local worklogs are provided using a delimiter-separated values format such as CSV then you will need to provide a `parse_delimited` section in the configuration file. An example `parse_delimited` section is shown below.

``` yaml
parse_delimited:
  col_labels:
    description: "task"
    start: "start"
    end: "end"
    duration: null
    tags: "tags"
  col_formats:
    start: "%Y-%m-%d %H:%M"
    end: "%Y-%m-%d %H:%M"
  delimiter2: ":"
  timezone: "US/Eastern"
  dialect: {}
```

There are up to 5 allowed entries in the `parse_delimited` mapping. The required fields are `col_labels` and `col_formats`, while the `delimiter2`,  `timezone`,  `dialect` can be omitted or `null`. 

* `col_labels`: a mapping of entries specifying the meaning of the relevant columns in the source data. Only 2 out of 3 of the columns corresponding to the worklogs `start`, `end`, and `duration`s are required (although all three can be provided).

    * `description`: a string specifying the name of the column providing the description of the worklog.
    * `start`: a string specifying the name of the column providing the start datetime of the worklogs (this can be omitted or `null`).
    * `end`: a string specifying the name of the column providing the end datetime of the worklogs (this can be omitted or `null`).
    * `duration`: a string specifying the name of the column providing the duration of the worklogs (this can be omitted or `null`).
    * `tags`: a string specifying the name of the column providing the tags for the worklogs. Tags are the mechanism that are used to identify which Jira issue, if any, that a given worklog corresponds to. A given worklog is allowed to have multiple tags, although only one tag can correspond to a Jira issue. If there are multiple tags then they are specified using a string that is separated by the `separator2` character.

#### Excel worklog parsing 


## Related software

TODO
