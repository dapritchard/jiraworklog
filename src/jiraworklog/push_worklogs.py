#!/usr/bin/env python3

from jiraworklog.delete_worklog import delete_worklog
from jiraworklog.diff_worklogs import create_augwkl_jira

# def update_worklogs(jira, checkedin, diff_local, diff_remote):
#     # Note that `checkedin` is modified in the call to `perform_update_actions`
#     update_instrs = create_update_instructions(diff_local, diff_remote)
#     perform_update_actions(jira, checkedin, update_instrs)
#     return checkedin

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
        checkedin[issue].append(augwkl['full'])
    else:
        found_match = False
        for i, augwkl_checkedin in enumerate(checkedin):
            if augwkl_checkedin['canon'] == augwkl['canon']:
                found_match = True
                checkedin.pop(i)
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
