#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.configuration import Configuration
import os
from typing import Optional


class AuthTokenMissingKeyError(RuntimeError):

    def __init__(self, key: str, env_key: str):
        msg = (
            "Jira authentication error.\n"
            "Attempting to authenticate using an API token.\n"
            f"The '{key}' value was not provided, nor was the {env_key} set."
        )
        super().__init__(msg)


def auth_jira(conf: Configuration) -> JIRA:
    if conf.auth_token:
        jira = JIRA(
            server=conf.auth_token['server'],
            basic_auth=(
                conf.auth_token['user'],
                conf.auth_token['api_token']
            )
        )
    else:
        msg = 'Only authentication via auth token is currently implemented'
        raise RuntimeError(msg)
    return jira


def make_get_auth_info(key):
    def get_auth_info(auth_token: dict[str, Optional[str]]) -> str:
        maybe_value = auth_token.get(key)
        if maybe_value:
            value = maybe_value
        else:
            env_key = envvar_tbl[key]
            maybe_envval = os.environ.get(env_key)
            if maybe_envval:
                value = maybe_envval
            else:
                raise AuthTokenMissingKeyError(key, env_key)
        return value
    envvar_tbl = {
        'server': 'JW_SERVER',
        'user': 'JW_USER',
        'api_token': 'JW_API_TOKEN'
    }
    return get_auth_info
