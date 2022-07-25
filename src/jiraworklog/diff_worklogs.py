#!/usr/bin/env python3

from jiraworklog.utils import map2_issues
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira


class Diffs:

    added: list[WorklogCanon]
    removed: list[WorklogCanon]

    def __init__(
        self,
        added: list[WorklogCanon],
        removed: list[WorklogCanon]
    ) -> None:
        self.added = added
        self.removed = removed


class DiffsLocal:

    added: list[WorklogCanon]
    removed: list[WorklogCheckedin]

    def __init__(
        self,
        added: list[WorklogCanon],
        removed: list[WorklogCheckedin]
    ) -> None:
        self.added = added
        self.removed = removed


class DiffsRemote:

    added: list[WorklogJira]
    removed: list[WorklogCheckedin]

    def __init__(
        self,
        added: list[WorklogJira],
        removed: list[WorklogCheckedin]
    ) -> None:
        self.added = added
        self.removed = removed


def diff_worklogs(
    wkls_other: dict[str, list[WorklogCanon]],
    wkls_checkedin: dict[str, list[WorklogCheckedin]]
) -> dict[str, Diffs]:
    # TODO: assert that they keys are identical for the two?
    diffed_worklogs = {
        k: diff_worklogs_singleissue(wkls_other[k], wkls_checkedin[k])
        for k
        in wkls_other.keys()
    }
    return diffed_worklogs


# The efficiency of this algorithm could likely by improved. However, note
# that we have to handle the possibility of duplicate worklog entries which
# precludes us from doing certain things like using sets
def diff_worklogs_singleissue(
    other_listwkl: list[WorklogCanon],
    checkedin_listwkl: list[WorklogCheckedin]
) -> Diffs:
    removed_other = []
    remaining_other = other_listwkl.copy()
    for checked_wkl in checkedin_listwkl:
        try:
            remaining_other.remove(checked_wkl)
        except:
            removed_other.append(checked_wkl)
    diffs_singleissue = Diffs(remaining_other, removed_other)
    return diffs_singleissue


def diff_local(
    local_wkls: dict[str, list[WorklogCanon]],
    checkedin_wkls: dict[str, list[WorklogCheckedin]]
) -> dict[str, DiffsLocal]:
    out = map2_issues(diff_local_listwkls, local_wkls, checkedin_wkls)
    return out

# The efficiency of this algorithm could likely by improved. However, note
# that we have to handle the possibility of duplicate worklog entries which
# precludes us from doing certain things like using sets
def diff_local_listwkls(
    local_listwkl: list[WorklogCanon],
    checkedin_listwkl: list[WorklogCheckedin]
) -> DiffsLocal:
    remaining_checkedin = []
    remaining_local = local_listwkl.copy()
    for checked_wkl in checkedin_listwkl:
        try:
            remaining_local.remove(checked_wkl)
        except:
            remaining_checkedin.append(checked_wkl)
    diffed_local_listwkls = DiffsLocal(remaining_local, remaining_checkedin)
    return diffed_local_listwkls


def diff_remote(
    remote_wkls: dict[str, list[WorklogJira]],
    checkedin_wkls: dict[str, list[WorklogCheckedin]]
) -> dict[str, DiffsRemote]:
    out = map2_issues(diff_remote_listwkls, remote_wkls, checkedin_wkls)
    return out


# NOTE: I think this is the same algorithm as for `diff_remote_listwkls`?
# The efficiency of this algorithm could likely by improved. However, note
# that we have to handle the possibility of duplicate worklog entries which
# precludes us from doing certain things like using sets
def diff_remote_listwkls(
    remote_listwkl: list[WorklogJira],
    checkedin_listwkl: list[WorklogCheckedin]
) -> DiffsRemote:
    remaining_remote = []
    remaining_checkedin = checkedin_listwkl.copy()
    for remote_wkl in remote_listwkl:
        try:
            remaining_checkedin.remove(remote_wkl)
        except:
            remaining_remote.append(remote_wkl)
    diffed_remote_listwkls = DiffsRemote(remaining_remote, remaining_checkedin)
    return diffed_remote_listwkls
