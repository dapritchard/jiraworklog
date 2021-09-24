#!/usr/bin/env python3

from fetch_worklogs import fetch_worklogs_remotedata
import json

def sync_worklogs(path_worktree, path_head, path_remote, jira):

    # Get the working tree issues. The issues contained therein determines which
    # issues are considered in HEAD and remote
    with open(path_worktree) as file:
        worktree = json.load(file)

    # Get the issues from the last sync. The HEAD file does not exist until the
    # first sync is performed. In the event that this is indeed the first time,
    # create a `issues_head` skeleton without any worklogs in it
    try:
        with open(path_head) as file:
            head = json.load(file)
    except:
        # TODO: check with the user to make sure that we are expecting to be
        # missing the HEAD file
        head = {k: [] for k in worktree.keys()}

    # Get the remote issues
    issue_keys = extract_issue_keys(worktree)
    remote = fetch_worklogs_remotedata(jira, issue_keys)

    # sync_worklogs_impl(worktree, head, remote)
    return [worktree, head, remote]


def sync_worklogs_impl(worktree, head, remote):

    def setdiff(list1, list2):
        return [i for i in list1 + list2 if i not in list2]

    def add_issues(worklogs, issue_namekeys):
        return None

    issue_keys_worktree = extract_issue_keys(worktree)
    issue_keys_head = extract_issue_keys(head)
    issue_namekeys_added = setdiff(issue_keys_worktree, issue_keys_head)
    issue_namekeys_removed = setdiff(issue_keys_head, issue_keys_worktree)


def extract_issue_keys(worklogs):
    return [x.split('@')[-1] for x in worklogs.keys()]
