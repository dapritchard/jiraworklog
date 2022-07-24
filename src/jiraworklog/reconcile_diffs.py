#!/usr/bin/env python3

from __future__ import annotations

from jiraworklog.diff_worklogs import Diffs
from jiraworklog.update_instructions import UpdateInstrs
from jiraworklog.utils import find
from jiraworklog.worklogs import WorklogCanon, WorklogCanon


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


def reconcile_diffs(
    diffs_local: dict[str, Diffs],
    diffs_remote: dict[str, Diffs],
    remote_wkls: dict[str, list[WorklogCanon]]
) -> UpdateInstrs:
    # TODO: assert that keys are identical?
    acc_added = create_empty_diffsaligned()
    acc_removed = create_empty_diffsaligned()
    for k in diffs_local.keys():
        rec_diffs = reconcile_diffs_singleissue(
            diffs_local[k],
            diffs_remote[k]
        )
        acc_added.extend(rec_diffs['added'])
        acc_removed.extend(rec_diffs['removed'])
    rmt_remove = map_local_to_jira(acc_removed.local, remote_wkls)
    update_instructions = UpdateInstrs(
        chk_add_listwkl=acc_added.aligned,
        chk_remove_listwkl=acc_removed.aligned,
        rmt_add_listwkl=acc_added.local,
        rmt_remove_listwkl=rmt_remove
    )
    return update_instructions


def reconcile_diffs_singleissue(
    diff_local: Diffs,
    diff_remote: Diffs
) -> dict[str, ReconciledDiffs]:
    added = find_aligned_extchanges(diff_local.added, diff_remote.added)
    removed = find_aligned_extchanges(
        diff_local.removed,
        diff_remote.removed
    )
    reconciled_diffs_singleissue = {
        'added': added,
        'removed': removed
    }
    return reconciled_diffs_singleissue


def find_aligned_extchanges(
    local_listwkl: list[WorklogCanon],
    remote_listwkl: list[WorklogCanon]
) -> ReconciledDiffs:
    # aligned = []
    # updated_local = []
    # remote_copy_listwkl = remote_listwkl.copy()
    # for local_wkl in local_listwkl:
    #     found_match = False
    #     for i, remote_wkl in enumerate(remote_copy_listwkl):
    #         if remote_wkl == local_wkl:
    #             found_match = True
    #             remote_copy_listwkl.pop(i)
    #             aligned.append(remote_wkl)
    #             continue
    #     if not found_match:
    #         updated_local.append(local_wkl)
    # return {
    #     'local': updated_local,
    #     'remote': diff_remote,
    #     'aligned': aligned
    # }
    updated_local = local_listwkl.copy()
    updated_remote = []
    aligned = []
    for remote_wkl in remote_listwkl:
        try:
            updated_local.remove(remote_wkl)
            aligned.append(remote_wkl)
        except:
            updated_remote.append(remote_wkl)
    diffs_aligned = ReconciledDiffs(updated_local, updated_remote, aligned)
    return diffs_aligned


def map_local_to_jira(
    local_listwkl: list[WorklogCanon],
    remote_wkls: dict[str, list[WorklogCanon]]
) -> list[WorklogCanon]:
    out = [
        find(wkl, remote_wkls[wkl.issueKey])
        for wkl
        in local_listwkl
    ]
    return out


def create_empty_diffsaligned() -> ReconciledDiffs:
    return ReconciledDiffs([], [], [])


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
