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
            f"The '{key}' value was not provided in the configuration file,\n"
            " nor was the '{env_key}' environmental variable set."
        )
        super().__init__(msg)


def auth_jira(conf: Configuration) -> JIRA:
    auth_token = conf.auth_token
    if auth_token:
        jira = JIRA(
            server=get_auth_server(auth_token),
            basic_auth=(
                get_auth_user(auth_token),
                get_auth_api_token(auth_token)
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


get_auth_server = make_get_auth_info('server')
get_auth_user = make_get_auth_info('user')
get_auth_api_token = make_get_auth_info('api_token')
