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
    # TODO: what does JIRA do if there's no issue of that name?
    worklogs = {k: [WorklogJira(x, k) for x in jira.worklogs(k)]
                for k
                in conf.issue_nms}
    return worklogs
