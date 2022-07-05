#!/usr/bin/env python3

def diff_local_worklogs(local, checkedin):
    pass

def diff_issue_worklogs(issue_local, issue_checkedin):
    def minimize(w):
        return {
            'comment': w['comment'],
            'started': w['started'],
            'timeSpentSeconds': w['timeSpentSeconds']
        }
    augm_checkedin = [(minimize(v), v) for v in issue_checkedin]
    added = []
    for w in issue_local:
        for i, a in enumerate(augm_checkedin):
            if w == a[0]:
                augm_checkedin.pop(i)
                both.append
                continue
        added.append(w)
    return {
        'added': added,
        'removed': augm_checkedin
    }
