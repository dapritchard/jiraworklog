#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.configuration import Configuration


def auth_jira(conf: Configuration) -> JIRA:
    jira = JIRA(
        server=conf.authentication['server'],
        basic_auth=(
            conf.authentication['user'],
            conf.authentication['api_token']
        )
    )
    return jira
