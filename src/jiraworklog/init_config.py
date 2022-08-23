#!/usr/bin/env python3

def init_config():
    init_config_impl()


def init_config_impl():

    print('What is your Jira author name? ', end='')
    author = input()


    print(
        "What is the Jira server's URL? (You can leave this blank if you "
        "intend to supply this value via the JW_SERVER environmental "
        "variable.) ",
        end=''
    )
    server = input()

    print(
        "What is your Jira user name? (You can leave this blank if you intend "
        "to supply this value via the JW_USER environmental variable.) ",
        end=''
    )
    user = input()

    print(
        "What is the Jira server's API token? (You can leave this blank if you "
        "intend to supply this value via the JW_API_TOKEN environmental "
        "variable.) ",
        end=''
    )
    api_token = input()
