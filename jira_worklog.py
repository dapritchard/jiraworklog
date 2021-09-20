#!/usr/bin/env python3

# Why does `jira.worklogs` require a network call? It seems like the issue
# already contains all of the data
def fetch_worklogs(jira, issue_nms):
    issues = fetch_issues(jira, issue_nms)
    worklogs = {(x.key, x.id): jira.worklogs(x) for x in issues}
    return fetch_worklogs_impl(worklogs)

def fetch_worklogs_impl(worklogs):
    return {k: [worklog_extract_fields(x) for x in v] for (k, v) in worklogs.items()}

def fetch_issues(jira, issue_nms):
    if not isinstance(issue_nms, list):
        raise Exception("'issue_nms' must be a list")
    if not all([isinstance(x, str) for x in issue_nms]):
        raise Exception("all elements of 'issue_nms' must be a string")
    return [jira.issue(nm) for nm in issue_nms]

def worklog_extract_fields(worklog):
    raw = worklog.raw
    return {
        'author': raw['author']['displayName'],
        'comment': raw['comment'],
        'created': raw['created'],
        'id': raw['id'],
        'issueId': raw['issueId'],
        'timeSpent': raw['timeSpent'],
        'timeSpentSeconds': raw['timeSpentSeconds'],
        'updateAuthor': raw['updateAuthor']['displayName'],
        'updated': raw['updated'],
    }
