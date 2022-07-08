#!/usr/bin/env python3

def diff_local_worklogs(local, checkedin):
    # TODO: assert that they keys are identical for the two?
    return {k: diff_issue_worklogs(local[k], checkedin[k])
            for k
            in local.keys()}

# The efficiency of this algorithm could likely by improved. However, note that
# we have to handle the possibility of duplicate worklog entries which precludes
# us from doing certain things like using sets
def diff_issue_worklogs(issue_local, issue_checkedin):
    def minimize(w):
        return {
            'comment': w['comment'],
            'started': w['started'],
            'timeSpentSeconds': w['timeSpentSeconds']
        }
    issue_augchk = [{'minimal': minimize(v), 'full': v}
                    for v
                    in issue_checkedin]
    added = []
    for wkl_local in issue_local:
        found_match = False
        for i, wkl_augchk in enumerate(issue_augchk):
            if wkl_local == wkl_augchk['minimal']:
                issue_augchk.pop(i)
                found_match = True
                continue
        if not found_match:
            added.append(wkl_local)
    return {
        'added': added,
        'removed': issue_augchk
    }
