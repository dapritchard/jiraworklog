#!/usr/bin/env python3

class CheckedinOSError(Exception):

    def __init__(self, checkedin_path: str) -> None:
        self.checkedin_path = checkedin_path

    def __str__(self):
        msg = (
            "Error reading the checked-in worklogs file at "
            f"'{self.checkedin_path}'\n\n{self.__cause__}"
        )
        return msg


class CheckedinJSONDecodeError(Exception):

    def __init__(self, checkedin_path: str) -> None:
        self.checkedin_path = checkedin_path

    def __str__(self):
        msg = (
            "Invalid JSON form of the checked-in worklogs file at "
            f"'{self.checkedin_path}'\n\n{self.__cause__}"
        )
        return msg


import argparse
import json
from jiraworklog.configuration import Configuration, check_default_checkedin_path, resolve_checkedin_path
# from jiraworklog.diff_worklogs import map_worklogs
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogCheckedin
from typing import Any

def read_checkedin_worklogs(
    conf: Configuration,
    cmdline_args: argparse.Namespace
    # actions: dict[str, Callable[..., Any]]
) -> dict[str, list[WorklogCheckedin]]:
    checkedin_path = resolve_checkedin_path(conf)
    try:
        with open(checkedin_path) as checkedin_file:
            worklogs_raw = json.load(checkedin_file)
    except FileNotFoundError:
        worklogs_raw = confirm_new_checkedin(checkedin_path, conf, cmdline_args)
    except OSError as exc:
        raise CheckedinOSError(checkedin_path) from exc
    except json.decoder.JSONDecodeError as exc:
        raise CheckedinJSONDecodeError(checkedin_path) from exc
    # TODO: validate contents (i.e. the form of the checkedin worklogs)
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
    conf: Configuration,
    cmdline_args: argparse.Namespace
) -> dict[str, Any]:

    # FIXME: for --dry-run this adds a file to the filesystem. Should we try to
    # remove it afterwards or just refuse to do it in the first place?
    if cmdline_args.auto_confirm or cmdline_args.dry_run:
        return {}

    # TODO: see https://docs.python.org/3/library/textwrap.html for a way to
    # properly wrap these paragraphs
    if check_default_checkedin_path(conf):
        # TODO: there is lot's of duplication in these paragraphs, let's try to
        # consolidate
        msg = (
            'jiraworklog stores a file on disk to track which worklogs that '
            'it is aware of, however it is unable to find the checked-in '
            'worklogs file in the default location of '
            "'~/.config/jiraworklog/checked-in-worklogs.json'. "
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
