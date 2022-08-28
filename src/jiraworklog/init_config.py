#!/usr/bin/env python3

import os
from textwrap import TextWrapper

MAXWIDTH=100


def init_config():
    init_config_impl()


def init_config_impl():

    textwrapper = TextWrapper(replace_whitespace=False)

    msg = (
        'What should the filepath be for the configuration file? (If you leave '
        "this blank it will default to '.jiraconfig.yaml'.) "
    )
    print_para(msg, textwrapper)
    config_path = input()
    if config_path == '':
        config_path = os.path.expanduser('~/.jwconfig.yaml')
    # TODO: try to write empty file to see if we have permission

    print('What is your Jira author name? ', end='')
    author = input()

    auth_type = 'token'

    msg = (
        "What is the Jira server's URL? (You can leave this blank if you "
        "intend to supply this value via the JW_SERVER environmental "
        "variable.) "
    )
    print_para(msg, textwrapper)
    server = input()

    msg = (
        "What is your Jira user name? (You can leave this blank if you intend "
        "to supply this value via the JW_USER environmental variable.) "
    )
    print_para(msg, textwrapper)
    user = input()

    msg = (
        "What is the Jira server's API token? (You can leave this blank if you "
        "intend to supply this value via the JW_API_TOKEN environmental "
        "variable.) "
    )
    print_para(msg, textwrapper)
    api_token = input()

    # TODO: issues_map

    # TODO: timezone. What happens if we upload without one?

    msg = (
        'What should the filepath be for the file that jiraworklog uses to '
        'store its worklog records? (You can leave this blank if you intend to '
        "supply the location via the '--config-file' command-line argument.) "
    )
    print_para(msg, textwrapper)
    checked_in_path = input()

    msg = (
        'What kind of filetype will you use to provide your worklog records '
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


def print_para(msg, textwrapper):
    width = min(MAXWIDTH, os.get_terminal_size().columns)
    textwrapper.width = width
    para = textwrapper.wrap(msg)
    if width - len(para[-1]) < 5:
        end = '\n'
    else:
        end = ' '
    print('\n'.join(para), end=end)
