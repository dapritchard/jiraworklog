#!/usr/bin/env python3

from typing import (Dict, List)

from jira import JIRA
from jiraworklog.configuration import Configuration
from jiraworklog.worklogs import WorklogJira

def read_remote_worklogs(jira: JIRA, conf: Configuration) -> Dict[str, List[WorklogJira]]:
    # TODO: error handling
    issues = {nm: jira.issue(nm) for nm in conf.issue_nms}
    worklogs = {k: jira.worklogs(v) for (k, v) in issues.items()}
    return worklogs
