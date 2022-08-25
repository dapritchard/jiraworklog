#!/usr/bin/env python3

import os
from textwrap import TextWrapper

MAXWIDTH=100


def init_config():
    init_config_impl()


def init_config_impl():

    textwrapper = TextWrapper(replace_whitespace=False)

    print('What is your Jira author name? ', end='')
    author = input()

    auth_type = 'token'

    msg = (
        "What is the Jira server's URL? (You can leave this blank if you "
        "intend to supply this value via the JW_SERVER environmental "
        "variable.) "    )
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

    # print(
    #     "What is the "
    # )


def print_para(msg, textwrapper):
    width = min(MAXWIDTH, os.get_terminal_size().columns)
    textwrapper.width = width
    para = textwrapper.wrap(msg)
    if width - len(para[-1]) < 5:
        end = '\n'
    else:
        end = ' '
    print('\n'.join(para), end=end)
