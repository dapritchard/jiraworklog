#!/usr/bin/env python3

from __future__ import annotations

import jira.resources as j
from typing import Any

from jiraworklog.utils import map_worklogs


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

    def to_canon(self) -> WorklogCanon:
        return self


class WorklogCheckedin(WorklogCanon):

    full: dict[str, str]

    def __init__(self, full: dict[str, str], issueKey: str) -> None:
        canon = full_to_canon(full)
        super().__init__(canon, issueKey)
        self.full = full

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, WorklogCheckedin):
            out = self.full == obj.full and super().__eq__(obj)
        else:
            out = super().__eq__(obj)
        return out

    def to_canon(self) -> WorklogCanon:
        return WorklogCanon(self.canon, self.issueKey)


class WorklogJira(WorklogCheckedin):

    jira: j.Worklog

    def __init__(self, jira_basewkl: j.Worklog, issueKey: str) -> None:
        full = jira_to_full(jira_basewkl)
        super().__init__(full, issueKey)
        self.jira = jira_basewkl

    def to_checkedin(self) -> WorklogCheckedin:
        return WorklogCheckedin(self.full, self.issueKey)


def jira_to_full(jira_basewkl: j.Worklog) -> dict[str, str]:
    raw = jira_basewkl.raw
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


def map_jira_to_canon(
    jira_wkls: dict[str, list[WorklogJira]]
) -> dict[str, list[WorklogCanon]]:
    canon_wkls = {
        k: [w.to_canon() for w in v]
        for k, v
        in jira_wkls.items()
    }
    return canon_wkls
