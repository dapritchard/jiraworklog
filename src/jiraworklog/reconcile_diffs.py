#!/usr/bin/env python3

from __future__ import annotations

from jiraworklog.diff_worklogs import DiffsLocal, DiffsRemote
from jiraworklog.update_instructions import UpdateInstructions
from jiraworklog.utils import find
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira


class ReconciledDiffs:

    local: list[WorklogCanon]
    remote: list[WorklogCanon]
    aligned: list[WorklogCanon]

    def __init__(
        self,
        local: list[WorklogCanon],
        remote: list[WorklogCanon],
        aligned: list[WorklogCanon]
    ) -> None:
        self.local = local
        self.remote = remote
        self.aligned = aligned

    def extend(self, other: ReconciledDiffs):
        self.local.extend(other.local)
        self.remote.extend(other.remote)
        self.aligned.extend(other.aligned)


class ReconciledAdded:

    local: list[WorklogCanon]
    remote: list[WorklogJira]
    aligned: list[WorklogJira]

    def __init__(
        self,
        local: list[WorklogCanon],
        remote: list[WorklogJira],
        aligned: list[WorklogJira]
    ) -> None:
        self.local = local
        self.remote = remote
        self.aligned = aligned

    def extend(self, other: ReconciledAdded):
        self.local.extend(other.local)
        self.remote.extend(other.remote)
        self.aligned.extend(other.aligned)


class ReconciledRemoved:

    local: list[WorklogCheckedin]
    remote: list[WorklogCheckedin]
    aligned: list[WorklogCheckedin]

    def __init__(
        self,
        local: list[WorklogCheckedin],
        remote: list[WorklogCheckedin],
        aligned: list[WorklogCheckedin]
    ) -> None:
        self.local = local
        self.remote = remote
        self.aligned = aligned

    def extend(self, other: ReconciledRemoved):
        self.local.extend(other.local)
        self.remote.extend(other.remote)
        self.aligned.extend(other.aligned)


def reconcile_diffs(
    diffs_local: dict[str, DiffsLocal],
    diffs_remote: dict[str, DiffsRemote],
    remote_wkls: dict[str, list[WorklogJira]]
) -> UpdateInstructions:
    acc_added = create_empty_reconcileadded()
    acc_removed = create_empty_reconcileremoved()
    # TODO: assert that keys are identical?
    for k in sorted(diffs_local.keys()):
        added = reconcile_added_listwkl(diffs_local[k].added, diffs_remote[k].added)
        removed = reconcile_removed_listwkl(diffs_local[k].removed, diffs_remote[k].removed)
        acc_added.extend(added)
        acc_removed.extend(removed)
    rmt_remove = map_checkedin_to_jira(acc_removed.local, remote_wkls)
    update_instructions = UpdateInstructions(
        chk_add_listwkl=acc_added.aligned,
        chk_remove_listwkl=acc_removed.aligned,
        rmt_add_listwkl=acc_added.local,
        rmt_remove_listwkl=rmt_remove
    )
    return update_instructions


# def recdiffs_singleissue(
#     diff_local: Diffs,
#     diff_remote: Diffs
# ) -> dict[str, ReconciledDiffs]:
#     added = rec_action(diff_local.added, diff_remote.added)
#     removed = rec_action(
#         diff_local.removed,
#         diff_remote.removed
#     )
#     reconciled_diffs_singleissue = {
#         'added': added,
#         'removed': removed
#     }
#     return reconciled_diffs_singleissue


# def rec_action(
#     local_listwkl: list[WorklogCheckedin],
#     remote_listwkl: list[WorklogCanon]
# ) -> ReconciledDiffs:
#     # aligned = []
#     # updated_local = []
#     # remote_copy_listwkl = remote_listwkl.copy()
#     # for local_wkl in local_listwkl:
#     #     found_match = False
#     #     for i, remote_wkl in enumerate(remote_copy_listwkl):
#     #         if remote_wkl == local_wkl:
#     #             found_match = True
#     #             remote_copy_listwkl.pop(i)
#     #             aligned.append(remote_wkl)
#     #             continue
#     #     if not found_match:
#     #         updated_local.append(local_wkl)
#     # return {
#     #     'local': updated_local,
#     #     'remote': diff_remote,
#     #     'aligned': aligned
#     # }
#     updated_local = local_listwkl.copy()
#     updated_remote = []
#     aligned = []
#     for remote_wkl in remote_listwkl:
#         try:
#             updated_local.remove(remote_wkl)
#             aligned.append(remote_wkl)
#         except:
#             updated_remote.append(remote_wkl)
#     diffs_aligned = ReconciledDiffs(updated_local, updated_remote, aligned)
#     return diffs_aligned

def reconcile_added_listwkl(
    local_listwkl: list[WorklogCanon],
    remote_listwkl: list[WorklogJira]
) -> ReconciledAdded:
    remaining_local = local_listwkl.copy()
    remaining_remote = []
    aligned = []
    for remote_wkl in remote_listwkl:
        try:
            remaining_local.remove(remote_wkl)
            aligned.append(remote_wkl)
        except:
            remaining_remote.append(remote_wkl)
    diffs_aligned = ReconciledAdded(remaining_local, remaining_remote, aligned)
    return diffs_aligned


# NOTE: this is the exact same algorithm as `reconcile_added_listwkl`
def reconcile_removed_listwkl(
    local_listwkl: list[WorklogCheckedin],
    remote_listwkl: list[WorklogCheckedin]
) -> ReconciledRemoved:
    remaining_local = local_listwkl.copy()
    remaining_remote = []
    aligned = []
    for remote_wkl in remote_listwkl:
        try:
            remaining_local.remove(remote_wkl)
            aligned.append(remote_wkl)
        except:
            remaining_remote.append(remote_wkl)
    diffs_aligned = ReconciledRemoved(remaining_local, remaining_remote, aligned)
    return diffs_aligned


def map_checkedin_to_jira(
    local_listwkl: list[WorklogCheckedin],
    remote_wkls: dict[str, list[WorklogJira]]
) -> list[WorklogJira]:
    out = [find(wkl, remote_wkls[wkl.issueKey]) for wkl in local_listwkl]
    return out


def create_empty_diffsaligned() -> ReconciledDiffs:
    return ReconciledDiffs([], [], [])

def create_empty_reconcileadded() -> ReconciledAdded:
    return ReconciledAdded([], [], [])

def create_empty_reconcileremoved() -> ReconciledRemoved:
    return ReconciledRemoved([], [], [])

# def flatten_update_instructions(nested_diffs):
#     flattened = []
#     for k_issue, v_issue in nested_diffs.items():
#         for k_where, v_where in v_issue.items():
#             for k_action, v_action in v_where.items():
#                 for augwkl in v_action:
#                     entry = {
#                         'remote': True if k_where == 'local' else False,
#                         'action': k_action,
#                         'issue': k_issue,
#                         'augwkl': augwkl
#                     }
#                     flattened.append(entry)
#     return flattened
