#!/usr/bin/env python3

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
