#!/usr/bin/env python3

import json

def merge_worklogs(path_worktree, path_head, path_remote):

    with open(path_worktree) as file: worklogs_worktree = json.load(file)
    with open(path_remote) as file: worklogs_remote = json.load(file)
    try:
        with open(path_head) as file: worklogs_local = json.load(file)
    except:
        # TODO: check with the user
        with open(path_head, "w") as file:
            json.dump(worklogs_worktree, file, indent=4)
            file.write("\n")

    merge_worklogs_impl(worklogs_worktree, worklogs_head, worklogs_remote)


def merge_worklogs_impl(worklogs_worktree, worklogs_local, worklogs_remote):

    return None


def extract_issue_keys(worklogs):
    issue_namekeys = worklogs.keys()
    return [x.split('@')[-1] for x in issue_namekeys]
