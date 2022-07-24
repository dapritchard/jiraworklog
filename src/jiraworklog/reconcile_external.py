#!/usr/bin/env python3

from __future__ import annotations

from jiraworklog.update_instructions import UpdateInstrs
from jiraworklog.worklogs import WorklogCanon, WorklogJira
from typing import Any


class DiffsAligned:

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

    def extend(self, other: DiffsAligned):
        self.local.extend(other.local)
        self.remote.extend(other.remote)
        self.aligned.extend(other.aligned)


# class UpdateInstrV2:

#     remote: bool
#     action: str
#     issue: str
#     worklog: Union[WorklogCanon, WorklogJira]

#     def __init__(
#         self,
#         remote: str,
#         action: str,
#         issue: str,
#         augwkl: WorklogCanon
#     ):
#         self.remote = True if remote == 'local' else False
#         self.action = action
#         self.issue = issue
#         self.worklog = augwkl


def create_empty_diffsaligned() -> DiffsAligned:
    return DiffsAligned([], [], [])

def reconcile_diffs(
    diffs_local: dict[str, dict[str, list[WorklogCanon]]],
    diffs_remote: dict[str, dict[str, list[WorklogJira]]],
    remote_wkls: dict[str, list[WorklogJira]]
) -> UpdateInstrs:
    # TODO: assert that keys are identical?
    acc_added = create_empty_diffsaligned()
    acc_removed = create_empty_diffsaligned()
    for k in diffs_local.keys():
        rec_diffs = reconcile_external_changes(
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

def map_local_to_jira(
    local_listwkl: list[WorklogCanon],
    remote_wkls: dict[str, list[WorklogJira]]
) -> list[WorklogJira]:
    out = [
        find(wkl, remote_wkls[wkl.issueKey])
        for wkl
        in local_listwkl
    ]
    return out

def find(val: Any, coll: list[Any]) -> Any:
    for elem in coll:
        if val == elem:
            return elem
    raise RuntimeError('Unable to find the provided value in the collection')

def reconcile_external_changes(
    diff_local: dict[str, list[WorklogCanon]],
    diff_remote: dict[str, list[WorklogJira]]
) -> dict[str, DiffsAligned]:
    added = find_aligned_extchanges(diff_local['added'], diff_remote['added'])
    removed = find_aligned_extchanges(
        diff_local['removed'],
        diff_remote['removed']
    )
    reconciled_external_changes = {
        'added': added,
        'removed': removed
    }
    return reconciled_external_changes

def find_aligned_extchanges(
    local_listwkl: list[WorklogCanon],
    remote_listwkl: list[WorklogJira]
) -> DiffsAligned:
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
    diffs_aligned = DiffsAligned(updated_local, updated_remote, aligned)
    return diffs_aligned

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
