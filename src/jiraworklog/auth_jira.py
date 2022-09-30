#!/usr/bin/env python3

from jira import JIRA, JIRAError
from jiraworklog.configuration import Configuration
import os
from typing import Optional
import prettyprinter
prettyprinter.install_extras(frozenset({'requests'}))


class AuthTokenMissingKeyError(Exception):

    def __init__(self, key: str, env_key: str):
        msg = (
            "Jira authentication error.\n"
            "Attempting to authenticate using an API token.\n"
            f"The '{key}' value was not provided in the configuration file,\n"
            " nor was the '{env_key}' environmental variable set."
        )
        super().__init__(msg)


class AuthTokenAuthError(Exception):

    auth_params: dict[str, str]
    jira_error: JIRAError

    def __init__(self, auth_params: dict[str, str], jira_error: JIRAError)-> None:
        self.auth_params = auth_params
        self.jira_error = jira_error

    def __str__(self) -> str:
        user, api_token = self.auth_params['basic_auth']
        msg = (
            "Jira authentication network error.\n"
            "Attempting to authenticate using an API token with the following "
            "credentials\n"
            "(the API token is partially obscured to protect your secrets):\n"
            f"    server:    '{self.auth_params['server']}'\n"
            f"    user:      '{user}'\n"
            f"    api_token: '{obscure_secret(api_token)}'\n"
            "\n"
            f"{fmt_jira_error(self.jira_error)}"
        )
        return msg


def auth_jira(conf: Configuration) -> JIRA:
    auth_token = conf.auth_token
    if auth_token:
        auth_params = {
            'server': get_auth_server(auth_token),
            'basic_auth': (
                get_auth_user(auth_token),
                get_auth_api_token(auth_token)
            )
        }
        try:
            jira = JIRA(**auth_params, validate=True)
        except JIRAError as exc:
            raise AuthTokenAuthError(auth_params, exc) from exc
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


def obscure_secret(s: str):
    n_remaining = 4
    n_obscure_digits = max(0, len(s) - n_remaining)
    obscured_s = '*' * n_obscure_digits + s[-n_remaining:]
    return obscured_s


# This is essentially copied over from the `JIRAError.__str__` method but using
# `prettyprinter.pformat` to format the request and response headers
def fmt_jira_error(jira_error: JIRAError) -> str:

    t = f"JiraError HTTP {jira_error.status_code}"
    if jira_error.url:
        t += f" url: {jira_error.url}"

    details = ""
    if jira_error.request is not None:
        if hasattr(jira_error.request, "headers"):
            msg = prettyprinter.pformat(jira_error.request.headers)
            details += f"\nrequest headers = {msg}"

        if hasattr(jira_error.request, "text"):
            details += f"\nrequest text = {jira_error.request.text}"
    if jira_error.response is not None:
        if hasattr(jira_error.response, "headers"):
            msg = prettyprinter.pformat(jira_error.response.headers)
            details += f"\nresponse headers = {msg}"

        if hasattr(jira_error.response, "text"):
            details += f"\nresponse text = {jira_error.response.text}"

    if jira_error.text:
        t += f"\ntext: {jira_error.text}"
    t += f"{details}"

    return t
