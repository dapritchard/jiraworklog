#!/usr/bin/env python3

from __future__ import annotations
from copy import deepcopy
from datetime import datetime

import jira as j
from jiraworklog.update_instructions import strptime_ptl
from jiraworklog.worklogs import WorklogCanon, jira_to_full
from typing import Any, Optional, Union


class JIRAMock(j.JIRA):

    entries: list[dict[str, dict[str, Union[str, datetime]]]]
    curr_id: int

    def __init__(self) -> None:
        self.entries = []
        self.curr_id=1000000

    def add_worklog(
            self,
            issue: str,
            timeSpentSeconds: str,
            comment: str,
            started: str
    ):
        wkl = {
            'issue': issue,
            'timeSpentSeconds': timeSpentSeconds,
            'comment': comment,
            'started': started
        }
        entry = {'action': 'add', 'worklog': wkl}
        self.entries.append(entry)
        jira_wkl_mock = JIRAWklMock(
            author='Daffy Duck',
            comment=comment,
            created='2021-10-03T17:21:55.764-0400',
            id=str(self.curr_id),
            issueId='',  # FIXME
            started=started,
            timeSpent='',  # FIXME
            timeSpentSeconds=timeSpentSeconds,
            updateAuthor='Daffy Duck',
            updated='2021-10-03T17:21:55.764-0400'
        )
        self.curr_id = self.curr_id + 1
        return jira_wkl_mock

    def clear(self) -> JIRAMock:
        self.entries = []
        return self


class JIRAWklMock(j.Worklog):

    raw: dict[str, Any]
    jiraclient: Optional[JIRAMock]

    def __init__(
        self,
        author: str,
        comment: str,
        created: str,
        id: str,
        issueId: str,
        started: str,
        timeSpent: str,
        timeSpentSeconds: str,
        updateAuthor: str,
        updated: str
    ):
        self.raw = {
            'author': {
                'displayName': author,
            },
            'comment': comment,
            'created': created,
            'id': id,
            'issueId': issueId,
            'started': started,
            'timeSpent': timeSpent,
            'timeSpentSeconds': int(timeSpentSeconds),
            'updateAuthor': {
                'displayName': updateAuthor,
            },
            'updated': updated
        }
        self.jiraclient = None


    def __repr__(self) -> str:
        return f"<JIRAMock Worklog: id='{self.raw['id']}'>"


    def set_jira(self, jiraclient: JIRAMock) -> JIRAWklMock:
        self.jiraclient = jiraclient
        return self


    def delete(self) -> None:
        if self.jiraclient is not None:
            entry = {'action': 'remove', 'worklog': jira_to_full(self)}
            self.jiraclient.entries.append(entry)
        else:
            msg = ('Tried to call `delete` without setting the `jiraclient` '
                   'attribute')
            raise RuntimeError(msg)


def to_addentry(
    local_listwkls: list[WorklogCanon]
) -> list[dict[str, dict[str, Union[str, datetime]]]]:
    def to_entry(wkl):
        worklog = {
            'issue': wkl.issueKey,
            'timeSpentSeconds': wkl.canon['timeSpentSeconds'],
            'comment': wkl.canon['comment'],
            'started': strptime_ptl(wkl.canon['started'])
        }
        return {'action': 'add', 'worklog': worklog}
    return [to_entry(w) for w in local_listwkls]
