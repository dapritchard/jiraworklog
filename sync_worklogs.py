#!/usr/bin/env python3

from jira.client import JIRA
from fetch_worklogs import fetch_worklogs_remotedata
import json


def sync_worklogs_import_data(path_worktree, path_head, path_remote, jira):

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

    # Get the remote issues. Throw an error if one of the issue keys was deleted
    # or never existed (i.e. was incorrectly specified)
    issue_keys_worktree = [extract_issue_key(k) for k in worktree.keys()]
    remote = fetch_worklogs_remotedata(jira, issue_keys_worktree)

    # TODO: step to normalize the worktree keys

    return [worktree, head, remote]


def sync_worklogs_create_altrep(worktree, head, remote):
    # head_filteredissues =
    return [
        issues_to_altrep(worktree, False),
        issues_to_altrep(head, True),
        issues_to_altrep(remote, True),
    ]


def sync_worklogs_construct_actions(worktree, head, remote):

    def setdiff(list1, list2):
        return [i for i in list1 + list2 if i not in list2]

    def normalize_head(head, issue_keys_worktree):
        head_nrm = {extract_issue_key(k): v
                    for (k, v) in head.items()
                    if k in issue_keys_worktree}
        curr_keys = head_nrm.keys()
        for k in issue_keys_worktree:
            if k not in curr_keys:
                head_nrm[k] = []
        return head_nrm

    issue_keys_worktree = extract_issue_keys(worktree)
    issue_keys_head = extract_issue_keys(head)
    dictkeys_map = {extract_issue_key(k): k for k in worktree.keys()}

    issue_namekeys_added = setdiff(issue_keys_worktree, issue_keys_head)
    issue_namekeys_removed = setdiff(issue_keys_head, issue_keys_worktree)

    # (i) Rename the dict keys from `"name@key"` form to `"key"` form in both
    # `worktree` and `head`, and (ii) for `head` add empty issues and remove
    # existing issues as necessary to match the issue set fourd in `worktree`
    worktree_nrm = {extract_issue_key(k): v for (k, v) in worktree.items()}
    head_nrm = normalize_head(head, issue_keys_worktree)
    remote_nrm = {extract_issue_key(k): v for (k, v) in remote.items()}

    altrep_worktree = issues_to_altrep(worktree_nrm, False)
    altrep_head = issues_to_altrep(head_nrm, True)
    altrep_remote = issues_to_altrep(remote_nrm, True)

    altissue_keys = (list(altrep_worktree.keys())
                     + list(altrep_head.keys())
                     + list(altrep_remote.keys()))
    unique_altissue_keys = list(set(altissue_keys))

    action_maybe_list = []
    for key in unique_altissue_keys:
        action_maybe = create_merged_maybe_entry(
            altrep_worktree.get(key, []),
            altrep_head.get(key, []),
            altrep_remote.get(key, [])
        )
        action_maybe_list.append(action_maybe)

    error_list = [x['value'] for x in action_maybe_list if x['is_error']]
    if len(error_list) > 0:
        raise RuntimeError('Something went wrong')

    action_list = [x['value'] for x in action_maybe_list if not x['is_error']]
    return action_list


class RemoteUpdateAdd:

    def __init__(self, existing, n_add, issueId, timeSpent, started, comment):
        self.existing = existing
        self.n_add = n_add
        self.issueId = issueId
        self.timeSpent = timeSpent
        self.started = started
        self.comment = comment

    def update(self, jira, issues, worklogs):
        del worklogs
        for _ in range(self.n_add):
            issue = jira.add_worklog(
                issue=issues['self.issueId'],
                timeSpent=self.timeSpent,
                started=self.started,
                comment=self.comment
            )
            self.existing.append(issue)
        return self.existing


class RemoteUpdateRemove:

    def __init__(self, existing, n_remove):
        self.existing = existing
        self.n_remove = n_remove

    def update(self, jira, issues, worklogs):
        del jira, issues
        for _ in range(self.n_remove):
            worklog_fields = self.existing.pop()
            worklog = worklogs[worklog_fields['id']]
            worklog.delete()
        return self.existing

def create_merged_maybe_entry(altrep_worktree, altrep_head, altrep_remote):

    n_worktree = len(altrep_worktree)
    n_head = len(altrep_head)
    n_remote = len(altrep_remote)

    # Enuerate all possible relationships
    if n_worktree == n_head == n_remote:
        None
    elif n_worktree == n_head < n_remote:
        None
    elif n_worktree == n_head > n_remote:
        None
    elif n_worktree < n_head == n_remote:
        None
    elif n_worktree < n_head < n_remote:
        None
    elif n_worktree < n_head > n_remote:
        None
    elif n_worktree > n_head == n_remote:
        None
    elif n_worktree > n_head < n_remote:
        None
    elif n_worktree > n_head > n_remote:
        None


def remote_entries_remove(worklogs, ids_to_remove):
    out = []
    for id in ids_to_remove:
        worklog = worklogs[id]
        out.append(worklog.delete())
    return out

def remote_entry_add(jira, issues, worklog_fields):
    worklog = jira.add_worklog(
        issue=issues[worklog_fields['issueId']],
        timeSpent=worklog_fields['timeSpent'],
        started=worklog_fields['started'],
        comment=worklog_fields['comment']
    )
    return worklog


def extract_issue_keys(issues):
    # [extract_issue_key(k) for k in issues.keys()]
    return [k for k in issues.keys()]


# It is assumed that the dict keys in `worklogs` are of the form `'name@key'`,
# so this function returns a list of the `"key"` portion of each dict key string
def extract_issue_key(dictkey):
    return dictkey.split('@')[-1]


def issues_to_altrep(issues, has_metadata):
    create_value = create_metadata_dict if has_metadata else lambda _: {}
    # def worklogs_to_dictrepr(worklogs):
    #     return {create_core_tuple(w): create_value(w) for w in worklogs}
    altrep = {}
    for (key, worklogs) in issues.items():
        for worklog in worklogs:
            new_key = create_core_tuple(worklog, key)
            new_value = create_value(worklog)
            if new_key in altrep:
                altrep[new_key].append(new_value)
            else:
                altrep[new_key] = [new_value]
    return altrep


def create_core_tuple(worklog, key):
    return (key,
            worklog['comment'],
            worklog['started'],
            worklog['timeSpentSeconds'])


def create_metadata_dict(worklog):
    keys = ['author', 'created', 'id', 'issueId', 'timeSpent',
            'updateAuthor', 'updated']
    return {k: worklog[k] for k in keys}








# def create_dictkey_canon(worktree_dictkeys, head_dictkeys, remote_dictkeys):

#     # Check if the remote issue ID string corresponds to the local issue ID
#     # string. `remote_str` is of the form `"name@key"`, while `"local_str"` may
#     # either be of the form `"name"` or `"name@key"`. In the former case compare
#     # the `"name"` portions against each other, while in the latter case compare
#     # the `"key"` portions against each other.
#     def check_match(remote_dictkey, local_dictkey):
#         remote_split_str = remote_dictkey.split("@")
#         local_split_str = local_dictkey.split("@")
#         has_local_key = (len(local_split_str) >= 1)
#         return (
#             remote_split_str[1] == local_split_str[1]
#             if has_local_key
#             else remote_split_str[0] == local_dictkey)

#     # Return the dict key in `local_dictkeys` corresponding to `remote_dictkey`
#     # if one can be found, or `None` if there is no match
#     def find_dictkey(remote_dictkey, local_dictkeys):
#         # https://stackoverflow.com/a/9868665/5518304
#         return next(
#             x for x in local_dictkeys if not check_match(remote_dictkey, x),
#             None)

#     local_dictkeys = list(set(worktree_dictkeys + head_dictkeys))
#     dictkey_map = {k: find_dictkey(k, remote_dictkeys) for k in local_dictkeys}
#     # # TODO: do we need this?
#     # for k in remote_dictkeys:
#     #     dictkey_map[k] = k
#     return dictkey_map



# # Make sure that the same set of issues are found in each dict with the same
# # keys
# #
# # The dict keys for `worktree` and possibly also for `head` for a given issue
# # may differ from the dict key for `remote` for the corresponding issue for one
# # of the following reasons.
# #     (i)  Only the issue name was provided for the working tree, so we need to
# #          append the issue key to the dict key.
# #     (ii) We already had both the issue name and the key, but now the name has
# #          changed on the remote so we need to update the dict key.
# # This is assumed to be a complete enumeration of the scenarios that could cause
# # the issue keys to differ.
# #
# # The issues in `remote` are assumed to be the full set of issues that we care
# # about since we grabbed them based on what issues are in `worktree`, and
# # furthermore the issue names and keys in the remote are the source of truth so
# # we simply need to make the keys for any corresponding issues in `worktree` and
# # `head` align with those.
# #
# # `head` might (i) have issues that aren't in `remote`, and it might also (ii)
# # be missing issues that are in remote. Any issues in `head` that are no longer
# # in `remote` (and by extension in `worktree` since the set of issues for those
# # two objects are assumed to be equal) are no longer needed and are therefore
# # removed. If we are missing issues in `head` that are in remote then we add
# # them with an empty worklog list.
# def align_issues(worktree, head, remote):

#     # Check if the remote issue ID string corresponds to the local issue ID
#     # string. `remote_str` is of the form `"name@key"`, while `"local_str"` may
#     # either be of the form `"name"` or `"name@key"`. In the former case compare
#     # the `"name"` portions against each other, while in the latter case compare
#     # the `"key"` portions against each other.
#     def check_match(remote_str, local_str):
#         remote_split_str = remote_str.split("@")
#         local_split_str = local_str.split("@")
#         has_local_key = (len(local_split_str) >= 1)
#         return (
#             remote_split_str[1] == local_split_str[1]
#             if has_local_key
#             else remote_split_str[0] == local_str)

#     # Return the dict key in `local_dictkeys` corresponding to `remote_dictkey`
#     # if one can be found, or `None` if there is no match
#     def find_dictkey(remote_dictkey, local_dictkeys):
#         # https://stackoverflow.com/a/9868665/5518304
#         return next(
#             x for x in local_dictkeys if not check_match(remote_dictkey, x),
#             None)

#     # Create a new dict with elements populated by the issues in `issues`
#     # corresponding to the dict keys in `dictkeys`. Note that this has two
#     # effects: (i) updating the keys in `issues`, and (ii) dropping any issues
#     # that don't correspond to a key in `dictkeys`
#     #
#     # There's surely a more efficient algorithm that can be used to
#     # perform this, but it may be the case that for the sizes of data we expect
#     # to encounter that this will be fast enough
#     def update_dictkeys(issues, dictkeys):
#         return {
#             k: issues.get(find_dictkey(k, dictkeys), []) for k in dictkeys}

#     remote_dictkeys = remote.keys()
#     worktree_newdictkeys = update_dictkeys(worktree, remote_dictkeys)
#     head_newdictkeys = update_dictkeys(head, remote_dictkeys)
#     return [worktree_newdictkeys, head_newdictkeys]
