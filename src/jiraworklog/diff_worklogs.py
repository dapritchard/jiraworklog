#!/usr/bin/env python3

from jiraworklog.worklogs import (
    WorklogCanon,
    WorklogCheckedin,
)


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


def diff_worklogs(
    wkls_other: dict[str, list[WorklogCanon]],
    wkls_checkedin: dict[str, list[WorklogCheckedin]]
) -> dict[str, dict[str, list[WorklogCanon]]]:
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
) -> dict[str, list[WorklogCanon]]:
    removed_other = []
    remaining_other = other_listwkl.copy()
    for checked_wkl in checkedin_listwkl:
        try:
            remaining_other.remove(checked_wkl)
        except:
            removed_other.append(checked_wkl)
    diffed_worklogs_singleissue = {
        'added': remaining_other,
        'removed': removed_other
    }
    return diffed_worklogs_singleissue
