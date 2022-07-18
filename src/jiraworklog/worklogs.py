#!/usr/bin/env python3

from typing import (Dict)
import jira.resources


class WorklogCanon:

    def __init__(self, canon: Dict[str, str]):
        self.canon = canon


class WorklogCheckedin(WorklogCanon):

    def __init__(self, full: Dict[str, str]):
        canon = {
            'comment': full['comment'],
            'started': full['started'],
            'timeSpentSeconds': full['timeSpentSeconds']
        }
        super().__init__(canon)
        self.full = full


class WorklogJira(WorklogCheckedin):

    def __init__(self, jira_wkl: jira.resources.Worklog):
        full = jira_to_full(jira_wkl)
        super().__init__(full)
        self.jira = jira_wkl


def jira_to_full(jira_wkl: jira.resources.Worklog) -> Dict[str, str]:
    raw = jira_wkl.raw
    full = {
        'author': raw['author']['displayName'],
        'comment': raw['comment'],
        'created': raw['created'],
        'id': raw['id'],
        'issueId': raw['issueId'],
        'started': raw['started'],
        'timeSpent': raw['timeSpent'],
        'timeSpentSeconds': str(raw['timeSpentSeconds']),
        'updateAuthor': raw['updateAuthor']['displayName'],
        'updated': raw['updated']
    }
    return full


def full_to_canon(full_wkl: Dict[str, str]) -> Dict[str, str]:
    canon = {
        'comment': full_wkl['comment'],
        'started': full_wkl['started'],
        'timeSpentSeconds': full_wkl['timeSpentSeconds']
    }
    return canon
