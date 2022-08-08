#!/usr/bin/env python3

from __future__ import annotations
from datetime import datetime

import jira as j
from jiraworklog.update_instructions import strptime_ptl
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira, jira_to_full
from typing import Any, Optional, Union


class JIRAMock(j.JIRA):

    # TODO: do we need the builder?
    entries: list[dict[str, dict[str, Union[str, datetime]]]]
    remote_wkls: dict[str, list[WorklogJira]]
    builder: BuildCheckedin

    def __init__(
        self,
        remote_wkls: Optional[dict[str, list[WorklogJira]]] = None,
        builder: Optional[BuildCheckedin] = None
    ) -> None:
        self.entries = []
        self.remote_wkls = {} if remote_wkls is None else remote_wkls
        self.builder = BuildCheckedin() if builder is None else builder

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

    # TODO: should this be a more faithful error message to the real JIRA type
    # if we give it a key that doesn't exist?
    def worklogs(self, issueKey):
        return self.remote_wkls[issueKey]

    def _set_remote_wkls(self, remote_worklogs):
        self.remote_wkls = remote_worklogs

    def clear(self) -> JIRAMock:
        self.entries = []
        self.builder.reset()
        return self


class BuildCheckedin():

    curr_id: int

    def __init__(self) -> None:
        self.curr_id=1000001

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
            issueId=issue,  # FIXME: should only contain digits? Do we care?
            started=started.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            timeSpent=to_dhms(timeSpentSeconds),
            timeSpentSeconds=timeSpentSeconds,
            updateAuthor='Daffy Duck',
            updated='2021-10-03T17:21:55.764-0400'
        )
        self.curr_id = self.curr_id + 1
        return jiramock_wkl

    def buildwkl(
        self,
        local_wkl: WorklogCanon
    ) -> JIRAWklMock:
        jiramock_wkl = self.build(
            issue=local_wkl.issueKey,
            timeSpentSeconds=local_wkl.canon['timeSpentSeconds'],
            comment=local_wkl.canon['comment'],
            started=strptime_ptl(local_wkl.canon['started'])
        )
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
        self.curr_id=1000001


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


# The type of the value of the inner dict in the return type is guaranteed to be
# `str` rather than `Union[str, datetime]`, but we make it more general so that
# we can concatenate the types later
def to_rementry(
    checkedin_listwkls: list[WorklogCheckedin]
) -> list[dict[str, dict[str, Union[str, datetime]]]]:
    entries = [
        {'action': 'remove', 'worklog': w.full}
        for w
        in checkedin_listwkls
    ]
    return entries


# TODO: verify that this is actually how Jira behaves
def to_dhms(seconds: str) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    chunks = []
    if d != 0: chunks.append(f'{d}d')
    if h != 0: chunks.append(f'{h}h')
    if m != 0: chunks.append(f'{m}m')
    if s != 0: chunks.append(f'{s}s')
    return ' '.join(chunks)
