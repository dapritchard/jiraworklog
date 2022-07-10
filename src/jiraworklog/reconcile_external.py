#!/usr/bin/env python3

from jiraworklog.delete_worklog import delete_worklog


def update_worklogs(jira, checkedin, diff_local, diff_remote):
    # Note that `checkedin` is modified in the call to `perform_update_actions`
    update_instrs = create_update_instructions(diff_local, diff_remote)
    perform_update_actions(jira, checkedin, update_instrs)
    return checkedin

def create_update_instructions(diff_local, diff_remote):
    nested_update_instrs = reconcile_external_changes(diff_local, diff_remote)
    update_instrs = flatten_update_instructions(nested_update_instrs)
    return update_instrs

def perform_update_actions(jira, checkedin, instructions):
    for instruction in instructions:
        if instruction.pop('remote'):
            update_remote(jira, **instruction)
        update_checkedin(checkedin, **instruction)
    return checkedin

def reconcile_external_changes(diff_local, diff_remote):
    added = find_aligned_extchanges(diff_local['added'], diff_remote['added'])
    removed = find_aligned_extchanges(
        diff_local['removed'],
        diff_remote['removed']
    )
    return {
        'checkedin': {
            'added': added['aligned'],
            'removed': removed['aligned']
        },
        'local': {
            'added': added['local'],
            'removed': removed['local']
        }
    }

def flatten_update_instructions(diffs):
    flattened = []
    for k_where, v_where in diffs.items():
        for k_action, v_action in v_where.items():
            for k_issue, v_issue in v_action.items():
                for augwkl in v_action:
                    entry = {
                        'remote': True if k_where == 'local' else False,
                        'action': k_action,
                        'issue': k_issue,
                        'augwkl': augwkl
                    }
                    flattened.append(entry)
    return flattened

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

def find_aligned_extchanges(diff_local, diff_remote):
    aligned = []
    updated_local = []
    for augwkl_local in diff_local:
        found_match = False
        for i, augwkl_remote in enumerate(diff_remote):
            if augwkl_remote['canon'] == augwkl_local['canon']:
                found_match = True
                diff_remote.pop(i)
                aligned.append(augwkl_remote)
                continue
        if not found_match:
            updated_local.append(augwkl_local)
    return {
        'local': updated_local,
        'remote': diff_remote,
        'aligned': aligned
    }

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
