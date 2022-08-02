#!/usr/bin/env python3

from __future__ import annotations
from datetime import datetime

import jira as j
from jiraworklog.update_instructions import strptime_ptl
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira, jira_to_full
from typing import Any, Optional, Union


class JIRAMock(j.JIRA):

    entries: list[dict[str, dict[str, Union[str, datetime]]]]
    builder: BuildCheckedin

    def __init__(self) -> None:
        self.entries = []
        self.builder = BuildCheckedin()

    def add_worklog(
            self,
            issue: str,
            timeSpentSeconds: str,
            comment: str,
            started: datetime
    ):
        wkl = {
            'issue': issue,
            'timeSpentSeconds': timeSpentSeconds,
            'comment': comment,
            'started': started
        }
        entry = {'action': 'add', 'worklog': wkl}
        self.entries.append(entry)
        jira_wkl_mock = self.builder.build(**wkl)
        return jira_wkl_mock


    def clear(self) -> JIRAMock:
        self.entries = []
        self.builder.reset()
        return self


class BuildCheckedin():

    curr_id: int

    def __init__(self) -> None:
        self.curr_id=1000000


    def build(
        self,
        issue: str,
        timeSpentSeconds: str,
        comment: str,
        started: datetime
    ) -> JIRAWklMock:
        jiramock_wkl = JIRAWklMock(
            author='Daffy Duck',
            comment=comment,
            created='2021-10-03T17:21:55.764-0400',
            id=str(self.curr_id),
            issueId=issue,  # FIXME
            started=started.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            timeSpent='',  # FIXME
            timeSpentSeconds=timeSpentSeconds,
            updateAuthor='Daffy Duck',
            updated='2021-10-03T17:21:55.764-0400'
        )
        self.curr_id = self.curr_id + 1
        return jiramock_wkl


    def build_listchk(self, canon_wkls: list[WorklogCanon]) -> list[JIRAMock]:
        checkedin_listwkls = []
        for wkl in canon_wkls:
            jiramock_basewkl = self.build(
                issue=wkl.issueKey,
                timeSpentSeconds=wkl.canon['timeSpentSeconds'],
                comment=wkl.canon['comment'],
                started=strptime_ptl(wkl.canon['started'])
            )
            jiramock_wkl = WorklogJira(jiramock_basewkl, wkl.issueKey)
            checkedin_listwkls.append(jiramock_wkl.to_checkedin())
        return checkedin_listwkls


    def reset(self) -> None:
        self.curr_id=1000000


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


# TODO: can we use the same routine that the mock class uses?
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


def to_rementry(
    checkedin_listwkls: list[WorklogCheckedin]
) -> list[dict[str, dict[str, str]]]:
    entries = [
        {'action': 'remove', 'worklog': w.full}
        for w
        in checkedin_listwkls
    ]
    return entries
