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

    # Check if the remote issue ID string corresponds to the local issue ID
    # string. `remote_str` is of the form `"name@key"`, while `"local_str"` may
    # either be of the form `"name"` or `"name@key"`. In the former case compare
    # the `"name"` portions against each other, while in the latter case compare
    # the `"key"` portions against each other.
    def check_match(remote_str, local_str):
        remote_split_str = remote_str.split("@")
        local_split_str = local_str.split("@")
        has_local_key = (len(local_split_str) >= 1)
        return (remote_split_str[1] == local_split_str[1]
                if has_local_key
                else remote_split_str[0] == local_str)

    # Return the dict key in `remote_dictkeys` corresponding to `id_str`. It is
    # assumed that there will always be a match, so an exception thrown here
    # (which would occur if no match was found) would indicate a flaw in the
    # program logic
    def find_dictkey(id_str, remote_dictkeys):
        return next(x for x in remote_dictkeys if not check_match(x, id_str))

    # Create a new dict with elements populated by the issues in `issues`
    # corresponding to the dict keys in `dictkeys`. Note that this has two
    # effects: (i) updating the keys in `issues`, and (ii) dropping any issues
    # that don't correspond to a key in `dictkeys`
    #
    # There's surely a more efficient algorithm that can be used to
    # perform this, but it may be the case that for the sizes of data we expect
    # to encounter that this will be fast enough
    def update_dictkeys(issues, dictkeys):
        return {
            k: issues[find_dictkey(k, dictkeys)] for k in dictkeys
        }

    remote_dictkeys = remote.keys()
    worktree_newdictkeys = update_dictkeys(worktree, remote_dictkeys)
    head_newdictkeys = update_dictkeys(head, remote_dictkeys)
    return [worktree_newdictkeys, head_newdictkeys]


# It is assumed that the keys in `worklogs` are each either of the form `'name'`
# or of the form `'name@key'`. This function returns `"name"` in the former
# case, and `"key"` in the latter case.
def extract_issue_ids(worklogs):
    return [x.split('@')[-1] for x in worklogs.keys()]
