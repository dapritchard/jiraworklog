#!/usr/bin/env python3

from jiraworklog.worklogs import WorklogCanon, WorklogJira
from typing import Union


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


class UpdateInstrV2:

    remote: bool
    action: str
    issue: str
    worklog: Union[WorklogCanon, WorklogJira]

    def __init__(
        self,
        remote: str,
        action: str,
        issue: str,
        augwkl: WorklogCanon
    ):
        self.remote = True if remote == 'local' else False
        self.action = action
        self.issue = issue
        self.worklog = augwkl


def create_update_instructions(
    diffs_local: dict[str, dict[str, list[WorklogCanon]]],
    diffs_remote: dict[str, dict[str, list[WorklogJira]]]
):
    # TODO: assert that keys are identical?
    nested_update_instrs = {
        k: reconcile_external_changes(diffs_local[k], diffs_remote[k])
        for k
        in diffs_local.keys()
    }
    update_instrs = flatten_update_instructions(nested_update_instrs)
    return update_instrs

def reconcile_external_changes(
    diff_local: dict[str, list[WorklogCanon]],
    diff_remote: dict[str, list[WorklogJira]]
):
    added = find_aligned_extchanges(diff_local['added'], diff_remote['added'])
    removed = find_aligned_extchanges(
        diff_local['removed'],
        diff_remote['removed']
    )
    return {
        'checkedin': {
            'added': added['aligned'],
            'removed': removed['aligned']
        },
        'local': {
            'added': added['local'],
            'removed': removed['local']
        }
    }

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

def flatten_update_instructions(nested_diffs):
    flattened = []
    for k_issue, v_issue in nested_diffs.items():
        for k_where, v_where in v_issue.items():
            for k_action, v_action in v_where.items():
                for augwkl in v_action:
                    entry = {
                        'remote': True if k_where == 'local' else False,
                        'action': k_action,
                        'issue': k_issue,
                        'augwkl': augwkl
                    }
                    flattened.append(entry)
    return flattened
