#!/usr/bin/env python3

from jiraworklog.diff_worklogs import (
    augm_wkls_local,
    augm_wkls_checkedin,
    augm_wkls_jira,
    diff_worklogs
)
from jiraworklog.reconcile_external import create_update_instructions
from jiraworklog.sync_worklogs import process_worklogs_pure


# Create mock JIRA class -------------------------------------------------------

class JIRAMock:

    def __init__(
        self,
        author: str,
        comment: str,
        created: str,
        id: str,
        issueId: str,
        started: str,
        timeSpent: str,
        timeSpentSeconds: int,
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
            'timeSpentSeconds': timeSpentSeconds,
            'updateAuthor': {
                'displayName': updateAuthor,
            },
            'updated': updated
        }

    def __repr__(self) -> str:
        return f"<JIRAMock Worklog: id='{self.raw['id']}'>"


# Create test data -------------------------------------------------------------

local_worklogs = {
    'P9992-3': [
        {
            'comment': 'Fracture negative control',
            'started': '2021-01-12T10:00:00.000-0500',
            'timeSpentSeconds': '60'
        },
        {
            'comment': 'Biweekly fracture CE meeting',
            'started': '2021-02-09T12:52:00.000-0500',
            'timeSpentSeconds': '1860'
        }
    ]
}

checkedin_worklogs = {
    'P9992-3': [
        {
            'author': 'Daffy Duck',
            'comment': 'Fracture negative control',
            'created': '2021-10-03T17:21:55.764-0400',
            'id': '15636',
            'issueId': '16977',
            'started': '2021-01-12T10:00:00.000-0500',
            'timeSpent': '1m',
            'timeSpentSeconds': '60',
            'updateAuthor': 'Daffy Duck',
            'updated': '2021-10-03T17:21:55.764-0400'
        },
        {
            'author': 'Daffy Duck',
            'comment': 'Specify fracture definitions',
            'created': '2021-10-03T17:22:21.438-0400',
            'id': '15679',
            'issueId': '16977',
            'started': '2021-01-12T11:00:00.000-0500',
            'timeSpent': '15m',
            'timeSpentSeconds': '900',
            'updateAuthor': 'Daffy Duck',
            'updated': '2021-10-03T17:22:21.438-0400'
        }
    ]
}

jira_99923_15601 = JIRAMock(
    author='Daffy Duck',
    comment='Project kick-off meeting',
    created='2021-10-03T17:20:03.553-0400',
    id='15601',
    issueId='16977',
    started='2021-01-11T09:00:00.000-0500',
    timeSpent='30m',
    timeSpentSeconds=1800,
    updateAuthor='Daffy Duck',
    updated='2021-10-03T17:20:03.553-0400'
)
jira_99923_15636 = JIRAMock(
    author='Daffy Duck',
    comment='Fracture negative control',
    created='2021-10-03T17:21:55.764-0400',
    id='15636',
    issueId='16977',
    started='2021-01-12T10:00:00.000-0500',
    timeSpent='1m',
    timeSpentSeconds=60,
    updateAuthor='Daffy Duck',
    updated='2021-10-03T17:21:55.764-0400'
)
jira_99923_15679 = JIRAMock(
    author='Daffy Duck',
    comment='Specify fracture definitions',
    created='2021-10-03T17:22:21.438-0400',
    id='15679',
    issueId='16977',
    started='2021-01-12T11:00:00.000-0500',
    timeSpent='15m',
    timeSpentSeconds=900,
    updateAuthor='Daffy Duck',
    updated='2021-10-03T17:22:21.438-0400'
)
remote_worklogs = {
    'P9992-3': [jira_99923_15601, jira_99923_15636, jira_99923_15679]
}


# Test routines ----------------------------------------------------------------

local_augwkls = augm_wkls_local(local_worklogs)
checkedin_augwkls = augm_wkls_checkedin(checkedin_worklogs)
remote_augwkls = augm_wkls_jira(remote_worklogs)

diffs_local = diff_worklogs(local_augwkls, checkedin_augwkls)
diffs_remote = diff_worklogs(remote_augwkls, checkedin_augwkls)
update_instrs = create_update_instructions(diffs_local, diffs_remote)

update_instructions = process_worklogs_pure(
    local_worklogs,
    checkedin_worklogs,
    remote_worklogs
)
