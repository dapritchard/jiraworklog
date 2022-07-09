#!/usr/bin/env python3

def create_actions_instructions(diff_local, diff_remote, iss_checkedin):
    updated_diffs = reconcile_external(diff_local, diff_remote)
    flat_diffs = create_flat_diffs(updated_diffs)
    return flat_diffs

def make_update_worklog(jira, checkedin, instructions):
    for instruction in instructions:
        is_remote = instruction.pop('remote')
        if is_remote:
            update_remote(jira, **instruction)
        update_checkedin(checkedin, **instruction)
    return checkedin

def update_checkedin(checkedin, action, issue, worklog):
    pass

def update_remote(jira, action, issue, worklog):
    pass

def create_flat_diffs(diffs):
    flattened = []
    for k_where, v_where in diffs.items():
        for k_action, v_action in v_where.items():
            for k_issue, v_issue in v_action.items():
                for augwkl in v_action:
                    entry = {
                        'remote': True if k_where == 'local' else False,
                        'action': k_action,
                        'issue': k_issue,
                        'worklog': augwkl
                    }
                    flattened.append(entry)
    return flattened

# def update_checkedin(iss_checkedin, args):
#     def update_checkedin_impl(iss_checkedin, update_fcn, iss_key, augwkl_local):


def add_checkedin(iss_checkedin, iss_key, augwkl_local):
    found_match = False
    for i, augwkl_checkedin in enumerate(iss_checkedin[iss_key]):
        if augwkl_checkedin['canon'] == augwkl_local['canon']:
            found_match = True
            iss_checkedin.pop(i)
            continue
    if not found_match:
        raise RuntimeError('Internal logic error. Please file a bug report')
    return None

def reconcile_external(diff_local, diff_remote):
    added = find_aligned(diff_local['added'], diff_remote['added'])
    removed = find_aligned(diff_local['removed'], diff_remote['removed'])
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

def find_aligned(diff_local, diff_remote):
    aligned = []
    updated_local = []
    for augwkl_local in worklogs_local:
        found_match = False
        for i, augwkl_remote in enumerate(diff_remote):
            if augwkl_remote['canon'] == augwkl_local['canon']:
                found_match = True
                diff_remote.pop(i)
                aligned.append(augwkl_remote)
                continue
        if not found_match:
            updated_local.append(augwkl_local)
    # return [updated_local, diff_remote, aligned]
    return {
        'local': updated_local,
        'remote': diff_remote,
        'aligned': aligned
    }
