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

# TODO: duplicate function in configuration.py. Let's try to remove this one
def extract_worklog_fields(worklog_jira):
    raw = worklog_jira.raw
    return {
        'author': raw['author']['displayName'],
        'comment': raw['comment'],
        'created': raw['created'],
        'id': raw['id'],
        'issueId': raw['issueId'],
        'started': raw['started'],
        'timeSpent': raw['timeSpent'],
        'timeSpentSeconds': str(raw['timeSpentSeconds']),
        'updateAuthor': raw['updateAuthor']['displayName'],
        'updated': raw['updated']
    }

# TODO: duplicate function in configuration.py. Let's try to remove this one
def worklog_full_to_canon(worklog_full):
    return {
        'comment': worklog_full['comment'],
        'started': worklog_full['started'],
        'timeSpentSeconds': worklog_full['timeSpentSeconds']
    }
