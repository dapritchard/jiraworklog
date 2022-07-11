#!/usr/bin/env python3

from jiraworklog.delete_worklog import delete_worklog
from jiraworklog.reconcile_external import create_update_instructions

# def update_worklogs(jira, checkedin, diff_local, diff_remote):
#     # Note that `checkedin` is modified in the call to `perform_update_actions`
#     update_instrs = create_update_instructions(diff_local, diff_remote)
#     perform_update_actions(jira, checkedin, update_instrs)
#     return checkedin

def push_worklogs(jira, checkedin, instructions):
    for instruction in instructions:
        if instruction.pop('remote'):
            update_remote(jira, **instruction)
        update_checkedin(checkedin, **instruction)
    return checkedin

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
    wkl = augwkl['canon']
    assert action in ['added', 'removed']
    if action == 'added':
        jira.add_worklog(
            issue=issue,
            timeSpent=wkl['timeSpent'],
            comment=wkl['comment']
        )
    else:
        delete_worklog(jira=jira, issue=issue)

# def add_checkedin(iss_checkedin, iss_key, augwkl_local):
#     found_match = False
#     for i, augwkl_checkedin in enumerate(iss_checkedin[iss_key]):
#         if augwkl_checkedin['canon'] == augwkl_local['canon']:
#             found_match = True
#             iss_checkedin.pop(i)
#             continue
#     if not found_match:
#         raise RuntimeError('Internal logic error. Please file a bug report')
