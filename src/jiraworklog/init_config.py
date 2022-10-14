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


def query_config(textwrapper: TextWrapper) -> dict[str, Any]:

    # msg = (
    #     "What kind of authentication will you use to access the Jira server?"
    #     "(You must enter one of either 'basic_auth' or 'oauth'.)"
    # )
    # print_para(msg, textwrapper)
    # auth_type = input()
    # while not auth_type in ['basic_auth', 'oauth']:
    #     msg = (
    #         "Invalid authentication type response. Please enter one of either "
    #         "'basic_auth' or 'oauth': "
    #     )
    #     auth_type = input()
    auth_type = "basic_auth"

    if auth_type == "basic_auth":
        basic_auth = query_basic_auth(textwrapper)
        open_auth = None
    else:
        raise RuntimeError("Haven't implemented OAuth yet")

    issues_map = query_issue_map(textwrapper)

    msg = (
        "What should the filepath be for the file that jiraworklog uses to "
        "store its worklog records? (You can leave this blank if you intend to "
        "use the default location of "
        "~/.config/jiraworklog/checked-in-worklogs.json.) "
    )
    print_para(msg, textwrapper)
    checked_in_path = input()
    if checked_in_path == "":
        checked_in_path = None

    msg = (
        "What kind of filetype will you use to provide your worklog records "
        "with? (You must enter one of either 'delimited' or 'excel'.)"
    )
    print_para(msg, textwrapper)
    parse_type = input()
    while not parse_type in ["delimited", "excel"]:
        msg = (
            "Invalid filetype response. Please enter one of either 'delimited' "
            "or 'excel': "
        )
        print_para(msg, textwrapper)
        parse_type = input()

    if parse_type == "delimited":
        parse_delimited = query_parse_delimited(textwrapper)
        parse_excel = None
    else:
        parse_delimited = None
        parse_excel = query_parse_excel(textwrapper)

    config = OrderedDict()
    config['jwconfig_version'] = "0.1.2"
    if basic_auth:
        config['basic_auth'] = basic_auth
    else:
        config['open_auth'] = open_auth
    config['issues_map'] = issues_map
    config['checked_in_path'] = checked_in_path
    if parse_delimited:
        config['parse_delimited'] = parse_delimited
    else:
        config['parse_excel'] = parse_excel
    return config


def query_basic_auth(textwrapper: TextWrapper) -> dict[str, Any]:

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

    basic_auth = OrderedDict(
        server=server,
        user=user,
        api_token=api_token
    )
    return basic_auth


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

    col_labels = query_col_labels(textwrapper)

    col_formats_delimited = query_col_formats_delimited(textwrapper)

    dialect = query_dialect(textwrapper)

    parse_delimited = OrderedDict(
        col_labels=col_labels,
        col_formats=col_formats_delimited
    )
    if len(dialect) >= 1:
        parse_delimited['dialect'] = dialect

    return parse_delimited


def query_parse_excel(textwrapper: TextWrapper) -> dict[str, Any]:

    col_labels = query_col_labels(textwrapper)

    col_formats_excel = query_col_formats_excel(textwrapper)

    parse_excel = OrderedDict(
        col_labels=col_labels,
        col_formats=col_formats_excel
    )

    return parse_excel


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
def query_col_formats_delimited(textwrapper: TextWrapper) -> dict[str, Any]:

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

    # TODO: provide an option to show the timezones
    msg = (
        "What is the timezone that you are in? (You can leave this blank if "
        "your worklogs already include timezone information.)"
    )
    print_para(msg, textwrapper)
    timezone = input()
    if timezone == "":
        timezone = None

    # msg = (
    #     "What is the format used to represent the worklog \"duration\" column "
    #     "datetime? See https://docs.python.org/3/library/datetime.html"
    #     "#strftime-and-strptime-format-codes for a definition of the format "
    #     "specification. (You can leave this blank if your worklogs don't "
    #     "include an duration time, but rather a start time and an end time.) "
    # )
    # print_para(msg, textwrapper)
    # duration = input()
    # if duration == "":
    #     duration = None

    msg = (
        "What is the delimiter that you use to separate tags in your worklog "
        "records entries? (You can leave this blank if you don't use a tag "
        "delimiter.)"
    )
    print_para(msg, textwrapper)
    delimiter2 = input()
    if delimiter2 == "":
        delimiter2 = None

    col_formats = OrderedDict(
        start=start,
        end=end,
        timezone=timezone,
        delimiter2=delimiter2
    )
    return col_formats


# TODO: we can assertain which columns to query and based on which are non-null
# when asking for names ask only for those
def query_col_formats_excel(textwrapper: TextWrapper) -> dict[str, Any]:

    # TODO: provide an option to show the timezones
    msg = (
        "What is the timezone that you are in? (You can leave this blank if "
        "your worklogs already include timezone information.)"
    )
    print_para(msg, textwrapper)
    timezone = input()
    if timezone == "":
        timezone = None

    # msg = (
    #     "What is the format used to represent the worklog \"duration\" column "
    #     "datetime? See https://docs.python.org/3/library/datetime.html"
    #     "#strftime-and-strptime-format-codes for a definition of the format "
    #     "specification. (You can leave this blank if your worklogs don't "
    #     "include an duration time, but rather a start time and an end time.) "
    # )
    # print_para(msg, textwrapper)
    # duration = input()
    # if duration == "":
    #     duration = None

    msg = (
        "What is the delimiter that you use to separate tags in your worklog "
        "records entries? (You can leave this blank if you don't use a tag "
        "delimiter.)"
    )
    print_para(msg, textwrapper)
    delimiter2 = input()
    if delimiter2 == "":
        delimiter2 = None

    col_formats = OrderedDict(
        timezone=timezone,
        delimiter2=delimiter2
    )
    return col_formats


def query_dialect(textwrapper: TextWrapper) -> dict[str, Any]:

    dialect = OrderedDict()

    msg = (
        "What is the delimiter that you use to separate your worklog entries? "
        "(Leave this blank to use the default delimiter of ','.)"
    )
    print_para(msg, textwrapper)
    delimiter = input()
    if delimiter != "":
        dialect['delimiter'] = delimiter

    # FIXME: add the remaining
    msg = (
        'The remaining dialect options haven\'t been added to the '
        'initialization script yet. Please add them directly to the '
        'configuration file.\n'
    )
    print_para(msg, textwrapper)

    return dialect


def print_para(msg, textwrapper):
    width = min(MAXWIDTH, os.get_terminal_size().columns)
    textwrapper.width = width
    para = [''] + textwrapper.wrap(msg)
    if width - len(para[-1]) < 5:
        end = '\n'
    else:
        end = ' '
    print('\n'.join(para), end=end)
