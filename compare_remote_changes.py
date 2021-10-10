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
    for update in modifications['updated']:
        subgraph_keys = subgraphs.keys()
        membersof = [k for k in subgraph_keys if check_in(update['keys'], k)]
        if len(membersof) == 0:
            subgraphs[tuple(update)] = [update]
        elif len(memborsof) == 1:
            # FIXME: THIS ISN"T RIGHT! Case: either the 'from' or 'to' worklogs are already present in a
            # subgraph, but not both
            if len(update) == 2:
                oldkey = membersof[0]
                newkey_elem = update[0] if update[0] in oldkey else update[1]
                newkey = (*oldkey, newkey_elem)
                newvalue = subgraphs[oldkey].append(update)
                del subgraphs[oldkey]
                subgraphs[newkey] = newvalue
            # Case:
            else
                pass
        else
            pass

        pass


# Create a dict with keys the worklog ID and values the "altrep" representation
# of the worklogs
def create_idrep(altrep):
    return {v['id']:k for (k, v) in altrep.values()}
