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
    issue_ids = extract_issue_ids(worktree)
    remote = fetch_worklogs_remotedata(jira, issue_ids)

    # sync_worklogs_impl(worktree, head, remote)
    return [worktree, head, remote]


def sync_worklogs_impl(worktree, head, remote):

    # Update the dict keys for `worktree` and `head` to make sure that given
    # issue has the same key for each of the dicts (unless the issue is absent
    # from 1 or 2 of the dicts). See the documentation for `align_issue_keys`
    # for details on why the keys might be out of sync
    worktree_newkeys, head_newkeys = align_issue_keys(worktree, head, remote)

    # At this point we assume that `worktree` and `remote` contain the same
    # issues, however `head`'s issues may totally differ

    def setdiff(list1, list2):
        return [i for i in list1 + list2 if i not in list2]

    def add_issues(worklogs, issue_namekeys):
        return None

    issue_keys_worktree = extract_issue_ids(worktree)
    issue_keys_head = extract_issue_ids(head)
    issue_namekeys_added = setdiff(issue_keys_worktree, issue_keys_head)
    issue_namekeys_removed = setdiff(issue_keys_head, issue_keys_worktree)


# The dict keys for `worktree` and possibly also for `head` for a given issue
# may differ from the dict key for `remote` for the corresponding issue for one
# of the following reasons.
#     (i)  Only the issue name was provided for the working tree, so we need to
#          append the issue key to the dict key.
#     (ii) We already had both the issue name and the key, but now the name has
#          changed on the remote so we need to update the dict key.
# This is assumed to be a complete enumeration of the scenarios that could cause
# the issue keys to differ.
#
# The issues in `remote` are assumed to be the full set of issues that we care
# about since we grabbed them based on what issues are in `worktree`, and
# furthermore the issue names and keys in the remote are the source of truth, so
# we simply need to make the keys for any corresponding issues in `worktree` and
# `head` align with those. Any issues in `head` that are no longer in `remote`
# (and by extension in `worktree` since the set of issues for those two objects
# are assumed to be equal) are no longer needed and are therefore removed.
def align_issue_keys(worktree, head, remote):


    return 1


# It is assumed that the keys in `worklogs` are each either of the form `'name'`
# or of the form `'name@key'`. This function returns `"name"` in the former
# case, and `"key"` in the latter case.
def extract_issue_ids(worklogs):
    return [x.split('@')[-1] for x in worklogs.keys()]
