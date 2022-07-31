#!/usr/bin/env python3

import jira.resources as j
from jiraworklog.worklogs import jira_to_full
from typing import Any, Optional


class JIRAMock:

    path: str
    entries: list[dict[str, dict[str, str]]]
    curr_id: int

    def __init__(
        self,
        path: str
    ) -> None:
        self.path = path

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


        # issue,
        # timeSpent: (Optional[str]) = None,
        # timeSpentSeconds: (Optional[str]) = None,
        # adjustEstimate: (Optional[str]) = None,
        # newEstimate: (Optional[str]) = None,
        # reduceBy: (Optional[str]) = None,
        # comment: (Optional[str]) = None,
        # started: (Optional[datetime.datetime]) = None,
        # user: (Optional[str]) = None,
class JIRAWklMock(j.Worklog):

    raw: dict[str, Any]
    jira: Optional[JIRAMock]

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
        self.jira = None

    def __repr__(self) -> str:
        return f"<JIRAMock Worklog: id='{self.raw['id']}'>"

    def delete(self) -> None:
        if self.jira is not None:
            entry = {'action': 'remove', 'worklog': jira_to_full(self)}
            self.jira.entries.append(entry)
        else:
            msg = 'Tried to call `delete` without setting `jira` attribute'
            raise RuntimeError(msg)
