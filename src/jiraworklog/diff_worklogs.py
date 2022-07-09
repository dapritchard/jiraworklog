#!/usr/bin/env python3

def diff_worklogs_local(local, checkedin):
    diff_worklogs = make_diff_worklogs(
        create_augiss_local,
        create_augiss_jira
    )
    return diff_worklogs(local, checkedin)

def diff_worklogs_jira(remote, checkedin):
    diff_worklogs = make_diff_worklogs(
        create_augiss_jira,
        create_augiss_jira
    )
    return diff_worklogs(remote, checkedin)

def make_diff_worklogs(create_augiss_checkedin, create_augiss_other):
    def diff_worklogs(dictof_issue_1, dictof_issue_2):
        # TODO: assert that they keys are identical for the two?
        return {k: diff_issue_worklogs(dictof_issue_1[k], dictof_issue_2[k])
                for k
                in dictof_issue_1.keys()}
    # The efficiency of this algorithm could likely by improved. However, note
    # that we have to handle the possibility of duplicate worklog entries which
    # precludes us from doing certain things like using sets
    def diff_issue_worklogs(issue_checkedin, issue_other):
        augiss_checkedin = create_augiss_checkedin(issue_checkedin)
        augiss_other = create_augiss_other(issue_other)
        added = []
        for wkl_other in augiss_other:
            found_match = False
            for i, wkl_checkedin in enumerate(augiss_checkedin):
                if wkl_checkedin['canon'] == wkl_other['canon']:
                    augiss_checkedin.pop(i)
                    found_match = True
                    continue
            if not found_match:
                added.append(wkl_other)
        return {
            'added': added,
            'removed': augiss_checkedin
        }
    return diff_worklogs

def create_augiss_jira(issue_local):
    def to_canon(w):
        return {
            'comment': w['comment'],
            'started': w['started'],
            'timeSpentSeconds': w['timeSpentSeconds']
        }
    augiss_jira = [{'canon': to_canon(wkl), 'full': wkl}
                    for wkl
                    in issue_local]
    return augiss_jira

def create_augiss_local(issue_local):
    augiss_local = [{'canon': wkl}
                    for wkl
                    in issue_local]
    return augiss_local
