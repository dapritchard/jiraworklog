#!/usr/bin/env python3

import json

def merge_worklogs(path_worktree, path_head, path_remote):

    with open(path_worktree) as file: issues_worktree = json.load(file)
    try:
        with open(path_head) as file: issues_local = json.load(file)
    except:
        # TODO: check with the user
        with open(path_head, "w") as file:
            json.dump(issues_worktree, file, indent=4)
            file.write("\n")
    # TODO: get keys from path_worktree and create `issues_remote` using a
    # temporary file (or use `fetch_issues_remotedata`?)

    merge_worklogs_impl(issues_worktree, issues_head, issues_remote)


def merge_worklogs_impl(issues_worktree, issues_head, issues_remote):

    def setdiff(list1, list2):
        return [i for i in list1 + list2 if i not in list2]

    def add_issues(worklogs, issue_namekeys):
        return None

    issue_keys_worktree = extract_issue_keys(issues_worktree)
    issue_keys_head = extract_issue_keys(issues_head)
    issue_namekeys_added = setdiff(issue_keys_worktree, issue_keys_head)
    issue_namekeys_removed = setdiff(issue_keys_head, issue_keys_worktree)


def extract_issue_keys(worklogs):
    return [x.split('@')[-1] for x in worklogs.keys()]
