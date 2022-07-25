#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.configuration import Configuration
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira
from typing import Union, Any

def read_remote_worklogs(
    jira: JIRA,
    conf: Configuration
) -> dict[str, list[WorklogJira]]:
    # TODO: error handling
    issues = {nm: jira.issue(nm) for nm in conf.issue_nms}
    worklogs = {k: [WorklogJira(x, k) for x in jira.worklogs(v)]
                for (k, v)
                in issues.items()}
    return worklogs
