#!/usr/bin/env python3

from collections import OrderedDict
import os
from textwrap import TextWrapper
from typing import Any

MAXWIDTH=100


def init_config():

    msg = (
        'What should the filepath be for the configuration file? (If you leave '
        "this blank it will default to '.jiraconfig.yaml'.) "
    )
    print_para(msg, textwrapper)
    config_path = input()
    if config_path == '':
        config_path = os.path.expanduser('~/.jwconfig.yaml')
    # TODO: try to write empty file to see if we have permission

    query_config()

    # TODO: write data to disk


def query_config():

    textwrapper = TextWrapper(replace_whitespace=False)

    # msg = (
    #     "What kind of authentication will you use to access the Jira server?"
    #     "(You must enter one of either 'token' or 'oauth'.)"
    # )
    # print_para(msg, textwrapper)
    # auth_type = input()
    # while not auth_type in ['token', 'oauth']:
    #     msg = (
    #         "Invalid authentication type response. Please enter one of either "
    #         "'token' or 'oauth': "
    #     )
    #     auth_type = input()
    auth_type = "token"

    if auth_type == "token":
        auth_token = query_auth_token(textwrapper)
        open_auth = None
    else:
        raise RuntimeError("Haven't implemented OAuth yet")

    issues_map = query_issue_map(textwrapper)

    msg = (
        "What should the filepath be for the file that jiraworklog uses to "
        "store its worklog records? (You can leave this blank if you intend to "
        "supply the location via the '--config-file' command-line argument.) "
    )
    print_para(msg, textwrapper)
    checked_in_path = input()
    if checked_in_path == "":
        checked_in_path = None

    msg = (
        "What kind of filetype will you use to provide your worklog records "
        "with? (You must enter one of either 'csv' or 'excel'.)"
    )
    print_para(msg, textwrapper)
    parse_type = input()
    while not parse_type in ['csv', 'excel']:
        msg = (
            "Invalid filetype response. Please enter one of either 'csv' or "
            "'excel': "
        )
        parse_type = input()


    parse_delimited = query_parse_delimited(textwrapper)
    parse_excel = None

    config = OrderedDict()
    if auth_token is None:
        config['open_auth'] = open_auth
    else:
        config['auth_token'] = auth_token
    config['issues_map'] = issues_map
    config['checked_in_path'] = checked_in_path
    if parse_delimited is None:
        config['parse_excel'] = parse_excel
    else:
        config['parse_delimited'] = parse_delimited
    return config


def query_auth_token(textwrapper: TextWrapper) -> dict[str, Any]:

    msg = (
        "What is the Jira server's URL? (You can leave this blank if you "
        "intend to supply this value via the JW_SERVER environmental "
        "variable.) "
    )
    print_para(msg, textwrapper)
    server = input()
    if server == "":
        server = None

    msg = (
        "What is your Jira user name? (You can leave this blank if you intend "
        "to supply this value via the JW_USER environmental variable.) "
    )
    print_para(msg, textwrapper)
    user = input()
    if user == "":
        user = None

    msg = (
        "What is the Jira server's API token? (You can leave this blank if you "
        "intend to supply this value via the JW_API_TOKEN environmental "
        "variable.) "
    )
    print_para(msg, textwrapper)
    api_token = input()
    if api_token == "":
        api_token = None

    auth_token = {
        "server": server,
        "user": user,
        "api_token": api_token
    }
    return auth_token


def query_issue_map(textwrapper: TextWrapper) -> dict[str, Any]:
    issue_map = OrderedDict()
    return issue_map


def query_parse_delimited(textwrapper: TextWrapper) -> dict[str, Any]:

    msg = (
        "What is the delimiter that you use to separate tags in your worklog "
        "records entries? (You can leave this blank if you don't use a tag "
        "delimiter.)"
    )
    print_para(msg, textwrapper)
    delimiter2 = input()
    if delimiter2 == "":
        delimiter2 = None

    col_labels = query_col_labels(textwrapper)

    col_formats = query_col_formats(textwrapper)

    parse_delimited = {
        "delimiter2" : delimiter2,
        "col_labels": col_labels,
        "col_formats": col_formats
    }
    return parse_delimited


def query_col_labels(textwrapper: TextWrapper) -> dict[str, Any]:

    msg = (
        "What is the name of the column that provides the worklog "
        "description? "
    )
    print_para(msg, textwrapper)
    description = input()
    if description == "":
        description = None

    msg = (
        "What is the name of the column that provides the worklog start time? "
        "(You can leave this blank if your worklogs don't include a start "
        "time, but rather an end time and a duration.) "
    )
    print_para(msg, textwrapper)
    start = input()
    if start == "":
        start = None

    msg = (
        "What is the name of the column that provides the worklog end time? "
        "(You can leave this blank if your worklogs don't include an end time, "
        "but rather a start time and a duration.) "
    )
    print_para(msg, textwrapper)
    end = input()
    if end == "":
        end = None

    msg = (
        "What is the name of the column that provides the worklog duration "
        "length? (You can leave this blank if your worklogs don't include a "
        "duration, but rather a start time and an end time.) "
    )
    print_para(msg, textwrapper)
    duration = input()
    if duration == "":
        duration = None

    msg = (
        "What is the name of the column that provides the worklog tags?"
    )
    print_para(msg, textwrapper)
    tags = input()
    if tags == "":
        tags = None

    col_labels = {
        "description": description,
        "start": start,
        "end": end,
        "duration": duration,
        "tags": tags
    }
    return col_labels


def query_col_formats(textwrapper: TextWrapper) -> dict[str, Any]:

    msg = (
        "TODO"
    )
    print_para(msg, textwrapper)
    start = input()
    if start == "":
        start = None

    msg = (
        "TODO"
    )
    print_para(msg, textwrapper)
    end = input()
    if end == "":
        end = None

    msg = (
        "TODO"
    )
    print_para(msg, textwrapper)
    duration = input()
    if duration == "":
        duration = None

    col_formats = {
        "start": start,
        "end": end,
        "duration": duration,
    }
    return col_formats


def print_para(msg, textwrapper):
    width = min(MAXWIDTH, os.get_terminal_size().columns)
    textwrapper.width = width
    para = textwrapper.wrap(msg)
    if width - len(para[-1]) < 5:
        end = '\n'
    else:
        end = ' '
    print('\n'.join(para), end=end)
