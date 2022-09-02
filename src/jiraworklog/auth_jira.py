#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.configuration import Configuration


def auth_jira(conf: Configuration) -> JIRA:
    jira = JIRA(
        server=conf.auth_token['server'],
        basic_auth=(
            conf.auth_token['user'],
            conf.auth_token['api_token']
        )
    )
    return jira
