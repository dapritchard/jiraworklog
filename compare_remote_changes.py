#!/usr/bin/env python3

def check_remote_changes(altrep_head, altrep_remote):

    idrep_head = create_idrep(altrep_head)
    idrep_remote = create_idrep(altrep_remote)
    ids = set().union(idrep_head.keys(), idrep_remote.keys())

    modifications = {'added': [], 'updated': [], 'removed': []}
    for id in ids:
        in_head = id in idrep_head.keys()
        in_remote = id in idrep_remote.keys()
        if in_head and not in_remote:
            modifications['removed'].append(idrep_head[id])
        elif not in_head and in_remote:
            modifications['added'].append(idrep_head[id])
        elif not idrep_head[id] == idrep_remote[id]:
            modifications['updated'].append([idrep_head[id], idrep_remote[id]])


def create_idrep(altrep):
    return {v['id']:k for (k, v) in altrep.values()}
