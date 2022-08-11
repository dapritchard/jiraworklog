#!/usr/bin/env python3

import json
from jiraworklog.configuration import Configuration
# from jiraworklog.diff_worklogs import map_worklogs
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogCheckedin
import os.path
from typing import Any, Callable

def read_checkedin_worklogs(
     conf: Configuration,
     actions: dict[str, Callable[..., Any]]
) -> dict[str, list[WorklogCheckedin]]:
    if conf.checked_in_path is None:
        is_default_path = True
        raw_path = ''
        checkedin_path = os.path.expanduser(
            '~/.config/jira-worklog/checked-in-worklogs.json'
        )
    else:
        is_default_path = False
        raw_path = conf.checked_in_path
        checkedin_path = os.path.expanduser(raw_path)
    try:
        with open(checkedin_path) as checkedin_file:
            worklogs_raw = json.load(checkedin_file)
    except:
        worklogs_raw = actions['confirm_new_checkedin'](
            checkedin_path,
            is_default_path
        )
    # TODO: validate contents
    align_checkedin_with_conf(worklogs_raw, conf)
    worklogs = map_worklogs_key(WorklogCheckedin, worklogs_raw)
    return worklogs


# TODO: move this and rename it since it's getting used by read_local_worklogs?
def align_checkedin_with_conf(
    worklogs: dict[str, Any],
    conf: Configuration
) -> dict[str, Any]:
    conf_nms = set(conf.issue_nms)
    checkedin_nms = set(worklogs.keys())
    added_nms = conf_nms - checkedin_nms
    removed_nms = checkedin_nms - conf_nms
    for nm in added_nms:
        worklogs[nm] = []
    if len(removed_nms) >= 1:
        # TODO: query user before removing
        for nm in removed_nms:
            del worklogs[nm]
    return worklogs


def unconditional_new_checkedin(
    _checkedin_path: str,
    _is_default_path: bool
) -> dict[str, dict[str, str]]:
    # Use of `del` here to satisfy the linter: https://stackoverflow.com/q/10025680
    del _checkedin_path
    del _is_default_path
    return {}


def confirm_new_checkedin(
    checkedin_path: str,
    is_default_path: bool
) -> dict[str, dict[str, str]]:
    # TODO: see https://docs.python.org/3/library/textwrap.html for a way to
    # properly wrap these paragraphs
    if is_default_path:
        msg = (
            'jiraworklog stores a file on disk to track which worklogs that '
            'it is aware of, however it is unable to find the checked-in '
            'worklogs file in the default location of '
            "'~/.config/jira-worklog/checked-in-worklogs.json'. "
            'If this is your first time running this application then '
            'you can ask jiraworklog to create a new file in the default '
            'location, otherwise you should exit and ensure that the correct '
            'location is specified.\n'
            'Do you want to create a new file to track worklogs? [y/n]: '
        )
    else:
        msg = (
            'jiraworklog stores a file on disk to track which worklogs that '
            'it is aware of, however it is unable to find the checked-in '
            'worklogs file in the location specified by your configuration '
            'file of '
            f"'{checkedin_path}'. "
            'If this is your first time running this application then '
            'you can ask jiraworklog to create a new file in the default '
            'location, otherwise you should exit and ensure that the correct '
            'location is specified.\n'
            'Do you want to create a new file to track worklogs? [y/n]: '
        )
    print(msg, end='')
    while True:
        response = input()
        if response == 'y':
            return {}
        elif response == 'n':
            raise RuntimeError('User specified exit')
        msg = (
            f"Invalid response '{response}'. Do you want to create a new file "
            'to track worklogs? [y/n]: '
        )
        print(msg, end='')
