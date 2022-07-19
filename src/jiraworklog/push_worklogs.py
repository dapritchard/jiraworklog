#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.delete_worklog import delete_worklog
from jiraworklog.diff_worklogs import create_augwkl_jira
from jiraworklog.sync_worklogs import strptime_ptl
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira
from functools import reduce
from typing import Any

# def update_worklogs(jira, checkedin, diff_local, diff_remote):
#     # Note that `checkedin` is modified in the call to `perform_update_actions`
#     update_instrs = create_update_instructions(diff_local, diff_remote)
#     perform_update_actions(jira, checkedin, update_instrs)
#     return checkedin


class PushWorklogs:

    checkedin: dict[str, list[WorklogCheckedin]]
    instr_checkedin_add: Any
    instr_checkedin_remove: Any
    instr_remote_add: Any
    instr_remote_remove: Any
    jira: JIRA

    def __init__(
        self,
        checkedin: dict[str, list[WorklogCheckedin]],
        instr_checkedin_add: Any,
        instr_checkedin_remove: Any,
        instr_remote_add: Any,
        instr_remote_remove: Any,
        jira: JIRA
    ) -> None:
        checkedin = checkedin,
        instr_checkedin_add = instr_checkedin_add,
        instr_checkedin_remove = instr_checkedin_remove,
        instr_remote_add = instr_remote_add,
        instr_remote_remove = instr_remote_remove,
        jira = jira


# TODO: is this better than what we had with the flat form?
def update_checkedin_add(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogJira
) -> dict[str, list[WorklogCheckedin]]:
    checkedin_wkls[jira_wkl.issueId].append(jira_wkl.to_checkedin())
    return checkedin_wkls

# TODO: is this better than what we had with the flat form?
def update_checkedin_remove(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogJira
) -> dict[str, list[WorklogCheckedin]]:
    checkedin_wkls[jira_wkl.issueId].remove(jira_wkl)
    return checkedin_wkls

# TODO: is this better than what we had with the flat form?
def push_worklog_add(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    canon_wkl: WorklogCanon,
    jira: JIRA
) -> dict[str, list[WorklogCheckedin]]:
    # TODO: add error handling?
    raw_jira_wkl = jira.add_worklog(
        issue=canon_wkl.issueId,
        timeSpentSeconds=canon_wkl.canon['timeSpentSeconds'],
        comment=canon_wkl.canon['comment'],
        started=strptime_ptl(canon_wkl.canon['comment'])
    )
    jira_wkl = WorklogJira(raw_jira_wkl)
    updated_wkls = update_checkedin_add(checkedin_wkls, jira_wkl)
    return updated_wkls

# TODO: is this better than what we had with the flat form?
def push_worklog_remove(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogJira
) -> dict[str, list[WorklogCheckedin]]:
    jira_wkl.jira.delete()
    updated_wkls = update_checkedin_remove(checkedin_wkls, jira_wkl)
    return updated_wkls

# TODO: is this better than what we had with the flat form?
def push_worklogs_v2(
    jira: JIRA,
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    update_instrs: PushWorklogs
):
    chk_1 = reduce(update_checkedin_add, update_instrs.instr_checkedin_add, checkedin_wkls)
    chk_2 = reduce(update_checkedin_remove, update_instrs.instr_checkedin_remove, chk_1)
    chk_3 = reduce(lambda x,y: push_worklog_add(x, y, jira), update_instrs.instr_remote_add, chk_2)
    chk_4 = reduce(push_worklog_remove, update_instrs.instr_remote_remove, chk_3)
    return chk_4

def push_worklogs(jira, checkedin, update_instrs):
    for instr in update_instrs:
        if instr.pop('remote'):
            maybe_jira_wkl = update_remote(jira, **instr)
            if maybe_jira_wkl is not None:
                instr['augwkl'] = create_augwkl_jira(maybe_jira_wkl)
        update_checkedin(checkedin, **instr)

def update_checkedin(checkedin, action, issue, augwkl):
    assert action in ['added', 'removed']
    if action == 'added':
        # TODO: consider sorting by start time?
        checkedin[issue].append(augwkl)
    else:
        found_match = False
        for i, augwkl_checkedin in enumerate(checkedin[issue]):
            if augwkl_checkedin['canon'] == augwkl['canon']:
                found_match = True
                del checkedin[issue][i]
                continue
        if not found_match:
            raise RuntimeError('Internal logic error. Please file a bug report')

def update_remote(jira, action, issue, augwkl):
    assert action in ['added', 'removed']
    if action == 'added':
        canon = augwkl['canon']
        maybe_jira_wkl = jira.add_worklog(
            issue=issue,
            timeSpentSeconds=canon['timeSpentSeconds'],
            comment=canon['comment']
        )
    else:
        full = augwkl['full']
        jira_wkl = jira.worklog(full['issueId'], full['id'])
        maybe_jira_wkl = jira_wkl.delete()
    return maybe_jira_wkl

# def add_checkedin(iss_checkedin, iss_key, augwkl_local):
#     found_match = False
#     for i, augwkl_checkedin in enumerate(iss_checkedin[iss_key]):
#         if augwkl_checkedin['canon'] == augwkl_local['canon']:
#             found_match = True
#             iss_checkedin.pop(i)
#             continue
#     if not found_match:
#         raise RuntimeError('Internal logic error. Please file a bug report')
