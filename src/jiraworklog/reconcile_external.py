#!/usr/bin/env python3

def create_update_instructions(diff_local, diff_remote):
    nested_update_instrs = reconcile_external_changes(diff_local, diff_remote)
    update_instrs = flatten_update_instructions(nested_update_instrs)
    return update_instrs

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

def flatten_update_instructions(nested_diffs):
    flattened = []
    for k_where, v_where in nested_diffs.items():
        for k_action, v_action in v_where.items():
            for k_issue, v_issue in v_action.items():
                for augwkl in v_issue:
                    entry = {
                        'remote': True if k_where == 'local' else False,
                        'action': k_action,
                        'issue': k_issue,
                        'augwkl': augwkl
                    }
                    flattened.append(entry)
    return flattened

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
