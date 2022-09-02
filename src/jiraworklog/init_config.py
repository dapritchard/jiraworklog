#!/usr/bin/env python3

from collections import OrderedDict
import os
from textwrap import TextWrapper
from typing import Any
import yaml

MAXWIDTH=100

# Add support for `OrderedDict`s. See
# https://stackoverflow.com/a/50181505/5518304
#
# TODO: it appears you can use regular dicts now: see
# https://stackoverflow.com/a/63126400/5518304
yaml.add_representer(
    OrderedDict,
    lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items())
)


def init_config():

    textwrapper = TextWrapper(replace_whitespace=False)

    # TODO: catch KeyboardInterrupt

    msg = (
        'What should the filepath be for the configuration file? (If you leave '
        "this blank it will default to '.jiraconfig.yaml'.) "
    )
    print_para(msg, textwrapper)
    config_path = os.path.expanduser(input())
    if config_path == '':
        config_path = os.path.expanduser('~/.jwconfig.yaml')

    # Try to obtain write access to the file to ensure that we have the proper
    # permissions before querying the user for information
    with open(config_path, 'a') as _:
        pass

    config = query_config(textwrapper)
    with open(config_path, 'w') as file:
        yaml_stanzas = []
        for k, v in config.items():
            yaml_stanzas.append(yaml.dump({k: v}))
        file.write('\n'.join(yaml_stanzas))


def query_config(textwrapper: TextWrapper):

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
    while not parse_type in ["csv", "excel"]:
        msg = (
            "Invalid filetype response. Please enter one of either 'csv' or "
            "'excel': "
        )
        print_para(msg, textwrapper)
        parse_type = input()

    if parse_type == "csv":
        parse_delimited = query_parse_delimited(textwrapper)
        parse_excel = None
    else:
        raise RuntimeError("not implemented yet")

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

    auth_token = OrderedDict(
        server=server,
        user=user,
        api_token=api_token
    )
    return auth_token


def query_issue_map(textwrapper: TextWrapper) -> dict[str, Any]:

    # prompt_local = (
    #     "Enter the name of one of your local worklog tags. Leave this blank if "
    #     "you are done entering local/remote tag pairs. "
    # )

    msg = (
       "In this section you will be asked to map the tags in your local "
        "worklogs to their corresponding worklog keys in Jira. You may add as "
        "many local/remote tag pairs as necessary."
    )
    print_para(msg, textwrapper)
    print('')

    issue_map = OrderedDict()
    while True:

        msg = (
            "Enter the name of one of your local worklog tags. Leave this "
            "blank if you are done entering local/remote tag pairs. "
        )
        print_para(msg, textwrapper)
        local_tag = input()
        if local_tag == '':
            break
        elif local_tag in issue_map:
            msg = (
                f"Warning: the entry '{local_tag}' has already been provided. "
                "This value will be ignored."
            )
            # TODO: remove leading \n?
            print_para(msg, textwrapper)
            continue

        msg = (
            "Enter the name of the remote worklog key corresponding to local "
            f"workings tagged by '{local_tag}'. "
        )
        print_para(msg, textwrapper)
        remote_key = input()

        issue_map[local_tag] = remote_key

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

    parse_delimited = OrderedDict(
        delimiter2=delimiter2,
        col_labels=col_labels,
        col_formats=col_formats
    )
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

    col_labels = OrderedDict(
        description=description,
        start=start,
        end=end,
        duration=duration,
        tags=tags
    )
    return col_labels


# TODO: we can assertain which columns to query and based on which are non-null
# when asking for names ask only for those
def query_col_formats(textwrapper: TextWrapper) -> dict[str, Any]:

    msg = (
        "What is the format used to represent the worklog \"start\" column "
        "datetime? See https://docs.python.org/3/library/datetime.html"
        "#strftime-and-strptime-format-codes for a definition of the format "
        "specification. (You can leave this blank if your worklogs don't "
        "include a start time, but rather an end time and a duration.) "
    )
    print_para(msg, textwrapper)
    start = input()
    if start == "":
        start = None

    msg = (
        "What is the format used to represent the worklog \"end\" column "
        "datetime? See https://docs.python.org/3/library/datetime.html"
        "#strftime-and-strptime-format-codes for a definition of the format "
        "specification. (You can leave this blank if your worklogs don't "
        "include an end time, but rather a start time and a duration.) "
    )
    print_para(msg, textwrapper)
    end = input()
    if end == "":
        end = None

    msg = (
        "What is the format used to represent the worklog \"duration\" column "
        "datetime? See https://docs.python.org/3/library/datetime.html"
        "#strftime-and-strptime-format-codes for a definition of the format "
        "specification. (You can leave this blank if your worklogs don't "
        "include an duration time, but rather a start time and an end time.) "
    )
    print_para(msg, textwrapper)
    duration = input()
    if duration == "":
        duration = None

    col_formats = OrderedDict(
        start=start,
        end=end,
        duration=duration,
    )
    return col_formats


def print_para(msg, textwrapper):
    width = min(MAXWIDTH, os.get_terminal_size().columns)
    textwrapper.width = width
    para = [''] + textwrapper.wrap(msg)
    if width - len(para[-1]) < 5:
        end = '\n'
    else:
        end = ' '
    print('\n'.join(para), end=end)
