# jiraworklog change log

## v0.1.1

* Fix an issue when creating a new checked-in worklogs file.
* Add a new `--init-config` command-line option that launches an interactive application for use in creating a new configuration file.


## v0.1.0

The project initial release. The following functionality is provided.

* Import user worklogs. Parsing of the worklogs is defined through a configuration file. The following formats are supported:
  * Delimiter-separated values format
  * Excel format
* Track worklogs that jiraworklog has uploaded to the specified Jira server by storing and updating a file in the user's filesystem.
* Make the appropriate changes to the worklogs on the Jira server to reflect changes in the user's worklogs.
