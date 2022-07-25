#!/usr/bin/env python3

from copy import deepcopy
from datetime import datetime
from jiraworklog.configuration import Configuration
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogCanon, jira_to_full
from jiraworklog.diff_worklogs import (
    # augm_wkls_local,
    # augm_wkls_checkedin,
    # augm_wkls_jira,
    # create_augwkl_jira,
    diff_worklogs,
    map_worklogs
)
# from jiraworklog.update_instructions import UpdateInstrs
from jiraworklog.read_remote_worklogs import read_remote_worklogs
from jiraworklog.reconcile_external import reconcile_diffs
from jiraworklog.sync_worklogs import process_worklogs_pure, strptime_ptl, sync_worklogs
from jiraworklog.utils import map_worklogs_key

# def strptime_ptl(datetime_str: str) -> datetime:
#     return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')

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


# ------------------------------------------------------------------------------

def delete_remote_worklog(worklog):
    try:
        worklog.jira.delete()
    except:
        # TODO: make a better error message
        raise RuntimeError('Failed to delete Jira worklog')

def upload_remote_worklog(jira, mock_remote_augwkl):
    full = mock_remote_augwkl.full
    jira_wkl = jira.add_worklog(
        issue=full['issueId'],
        timeSpent=full['timeSpent'],
        started=strptime_ptl(full['started']),
        comment=full['comment']
    )
    return jira_wkl

def sync_testdata_to_remote(jira, mock_remote_wkls):
    def upload_remote_worklog_ptl(mock_remote_wkl, issueKey):
        jira_wkl = upload_remote_worklog(jira, mock_remote_wkl)
        return WorklogCanon(jira_wkl, issueKey)
    conf = create_conf(list(mock_remote_wkls.keys()))
    remote_worklogs = read_remote_worklogs(jira, conf)
    map_worklogs(delete_remote_worklog, remote_worklogs)
    return map_worklogs_key(upload_remote_worklog_ptl, mock_remote_wkls)


def create_conf(issue_nms: list[str]) -> Configuration:
    issues_map = {str(i):v for i, v in enumerate(issue_nms)}  # create dummy issue keys to go with real issue names
    raw = {
        'author': '',
        'issues_map': issues_map,
        'parse_type': 'csv',
        'parse_delimited': {
            'delimiter2': ':',
            'col_labels': {
                'description': 'task',
                'start': 'start',
                'end': 'end',
                'duration': None,
                'tags': 'tags'
            },
            'col_formats': {
                'start': '%Y-%m-%d %H:%M',
                'end': '%Y-%m-%d %H:%M',
                'duration': None
            }
        }
    }
    conf = Configuration(raw)
    return conf


# Create test data -------------------------------------------------------------

raw_local_worklogs = {
    'P9992-3': [
        {
            'comment': 'Fracture negative control',
            'started': '2021-01-12T10:00:00.000-0500',
            'timeSpentSeconds': '60'
        },
        {
            'comment': 'Biweekly fracture CE meeting',
            'started': '2021-02-09T12:52:00.000-0500',
            'timeSpentSeconds': '1800'
        }
    ]
}
local_worklogs = {
    k: [WorklogCanon(w, k) for w in v]
    for k, v
    in raw_local_worklogs.items()
}

raw_checkedin_worklogs = {
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
checkedin_worklogs = map_worklogs_key(WorklogCheckedin, raw_checkedin_worklogs)


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
raw_remote_worklogs = {
    'P9992-3': [jira_99923_15601, jira_99923_15636, jira_99923_15679]
}
remote_worklogs = map_worklogs_key(WorklogCanon, raw_remote_worklogs)

# conf = create_conf(remote_worklogs.keys())


def update_checkedin_ids_wkls(remote_wkls, checkedin_wkls):
    # TODO: assert that they keys are identical for the two?
    wkls = {
        k: update_checkedin_ids_wkls_singleiss(remote_wkls[k], checkedin_wkls[k])
        for k
        in remote_wkls.keys()
    }
    return wkls

def update_checkedin_ids_wkls_singleiss(remote_listwkls, checkedin_listwkls):
    chk_copy_listwkls = checkedin_listwkls.copy()
    for remote_wkl in remote_listwkls:
        for i, checkedin_wkl in enumerate(chk_copy_listwkls):
            if checkedin_wkl == remote_wkl:
                chk_copy_listwkls[i] = WorklogCheckedin(remote_wkl.full, remote_wkl.issueKey)
                break
    return chk_copy_listwkls



# Test routines ----------------------------------------------------------------

# # Non-Jira testing
# local_augwkls = augm_wkls_local(local_worklogs)
# checkedin_augwkls = augm_wkls_checkedin(checkedin_worklogs)
# remote_augwkls = sync_testdata_to_remote(jira, augm_wkls_jira(remote_worklogs))

# Jira testing
upd_remote_wkls = sync_testdata_to_remote(jira, remote_worklogs)
upd_checkedin_wkls = update_checkedin_ids_wkls(upd_remote_wkls, checkedin_worklogs)

# Basically running `update_instrs` manually
diffs_local = diff_worklogs(local_worklogs, upd_checkedin_wkls)
diffs_remote = diff_worklogs(upd_remote_wkls, upd_checkedin_wkls)
update_instrs = reconcile_diffs(diffs_local, diffs_remote, upd_remote_wkls)

chk_copy = deepcopy(upd_checkedin_wkls)
update_instrs.push_worklogs_v2(jira, chk_copy)
