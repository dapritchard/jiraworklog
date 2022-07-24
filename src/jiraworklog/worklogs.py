#!/usr/bin/env python3

import jira.resources as j
from typing import Any


class WorklogCanon:

    canon: dict[str, str]
    issueKey: str

    def __init__(self, canon: dict[str, str], issueKey: str) -> None:
        self.canon = canon
        self.issueKey = issueKey

    def __eq__(self, obj: Any) -> bool:
        return (
            isinstance(obj, WorklogCanon)
            and (self.canon == obj.canon)
            and (self.issueKey == obj.issueKey)
        )

    def __ne__(self, obj: Any) -> bool:
        return not self == obj

class WorklogCheckedin(WorklogCanon):

    full: dict[str, str]

    def __init__(self, full: dict[str, str], issueKey: str) -> None:
        canon = full_to_canon(full)
        super().__init__(canon, issueKey)
        self.full = full


class WorklogJira(WorklogCheckedin):

    jira: j.Worklog

    def __init__(self, jira_wkl: j.Worklog, issueKey: str) -> None:
        full = jira_to_full(jira_wkl)
        super().__init__(full, issueKey)
        self.jira = jira_wkl

    def to_checkedin(self) -> WorklogCheckedin:
        return WorklogCheckedin(self.full, self.issueKey)


def jira_to_full(jira_wkl: j.Worklog) -> dict[str, str]:
    raw = jira_wkl.raw
    full = {
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
    return full


def full_to_canon(full_wkl: dict[str, str]) -> dict[str, str]:
    canon = {
        'comment': full_wkl['comment'],
        'started': full_wkl['started'],
        'timeSpentSeconds': full_wkl['timeSpentSeconds']
    }
    return canon
