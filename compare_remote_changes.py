#!/usr/bin/env python3

def check_remote_changes(altrep_head, altrep_remote):

    # Return True if any elements of `look_for` are in `look_in`, and return
    # False otherwise
    def check_in(look_for, look_in):
        for obj in look_for:
            if obj in look_in:
                return True
        return False

    idrep_head = create_idrep(altrep_head)
    idrep_remote = create_idrep(altrep_remote)
    ids = set().union(idrep_head.keys(), idrep_remote.keys())

    # Create a dict with each element a list of sublists such that each sublist
    # is a lenth-1 list (in the case of `'added'` and `'removed'`) or length-2
    # list (in the case of `'updated'`) of worklog altrep keys
    #
    # Note that for the `not idrep_head[id] == idrep_remote[id]` case we can
    # assume that the worklog is in both head and remote
    modifications = {'added': [], 'updated': [], 'removed': []}
    for id in ids:
        in_head = id in idrep_head.keys()
        in_remote = id in idrep_remote.keys()
        if in_head and not in_remote:
            modifications['removed'].append([idrep_head[id]])
        elif not in_head and in_remote:
            modifications['added'].append([idrep_head[id]])
        elif not idrep_head[id] == idrep_remote[id]:
            modifications['updated'].append([idrep_head[id], idrep_remote[id]])

    subgraphs = {}
    for modkey in ['added', 'updated', 'removed']:
        for altkeys in modifications[modkey]:
            subgraph_keys = subgraphs.keys()
            membersof = [k for k in subgraph_keys if check_in(altkeys, k)]
            if len(membersof) == 0:
                subgraphs[tuple(altkeys)] = {
                    'added': [],
                    'updated': [],
                    'removed': []
                }
                subgraphs[tuple(altkeys)][modkey].append(altkeys)
            elif len(altkeys) == 1:
                subgraphs[membersof[0]][modkey].append(altkeys)
            elif len(membersof) == 2:
                subgraph_0 = subgraphs[membersof[0]]
                subgraph_1 = subgraphs[membersof[1]]
                newkey = (*membersof[0], *membersof[1])
                newval = {
                    'added': subgraph_0['added'] ++ subgraph_1['added'],
                    'updated': subgraph_0['updated'] ++ subgraph_1['updated'],
                    'removed': subgraph_0['removed'] ++ subgraph_1['removed']
                }
                newval[modkey].append(altkeys)
                del subgraphs[membersof[0]]
                del subgraphs[membersof[1]]
                subgraphs[newkey] = newval
            elif altkeys[0] in membersof[0] and altkeys[1] in membersof[0]:
                subgraphs[membersof[0]][modkey].append(altkeys)
            # Case:  either the 'from' or 'to' worklogs are already present
            # in a subgraph, but not both
            else:
                newkey_elem = (altkeys[0]
                                if altkeys[0] in membersof[0]
                                else altkeys[1])
                newkey = (*membersof[0], newkey_elem)
                newvalue = subgraphs[membersof[0]][modkey].append(altkeys)
                del subgraphs[membersof[0]]
                subgraphs[newkey] = newvalue


# Create a dict with keys the worklog ID and values the "altrep" representation
# of the worklogs
def create_idrep(altrep):
    return {v['id']:k for (k, v) in altrep.values()}
