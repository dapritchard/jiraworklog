#!/usr/bin/env python3

import json
import os

from jiraworklog.utils import map_worklogs
from jiraworklog.update_instructions import strptime_ptl
from jiraworklog.update_instructions import UpdateInstructions
from pprint import pformat
from deepdiff import DeepDiff
from tests.jiramock import JIRAMock, JIRAWklMock
from tests.run_application import run_application
from typing import Any, Optional, Tuple


# def assert_golden(expected_path: str, actual_path: str) -> None:
#     diff = calc_diff(expected_path, actual_path)
#     if len(diff) >= 1:
#         msg = ''.join(diff)
#         raise RuntimeError(msg)


# def calc_diff(path_1: str, path_2: str):
#     with open(path_1, 'r') as file_1:
#         with open(path_2, 'r') as file_2:
#             diff = difflib.unified_diff(
#                 file_1.readlines(),
#                 file_2.readlines(),
#                 fromfile=path_1,
#                 tofile=path_2,
#             )
#     return list(diff)

def assert_diff(expected: Any, actual: Any) -> None:
    diff = DeepDiff(expected, actual)
    if diff != {}:
        msg = pformat(diff)
        raise RuntimeError(f'\n{msg}')


def create_apptest(input_dir):
    def test():
        jira, checkedin_full, _ = exercise_system(input_dir, ['--auto-confirm'])
        gld_rcmds, gld_chk = read_golden(input_dir)
        assert_diff(gld_rcmds, jira.entries)
        assert_diff(gld_chk, checkedin_full)
    return test


def exercise_system(
    input_dir: str,
    args: Optional[list[str]] = None
) -> Tuple[JIRAMock, dict[str, Any], UpdateInstructions]:
    inpaths = resolve_inpaths(input_dir)
    upd_args = (
        [inpaths['worklogs'], '--config-path', inpaths['config']]
        + ([] if args is None else args)
    )
    out = run_application(
        args=upd_args,
        checkedin_inpath=inpaths['checkedin'],
        mockremote_inpath=inpaths['checkedin']
    )
    return out


def resolve_inpaths(input_dir: str) -> dict[str, str]:
    def find_remote_path(dir_path):
        for s in os.listdir(dir_path):
            if s.startswith('worklogs.'):
                return input_dir + s
        return 'nonexistent-worklogs.txt'
    inpaths = {
        'config': input_dir + 'config.yaml',
        'worklogs': find_remote_path(input_dir),
        'checkedin': input_dir + 'checkedin.json',
        'remote': input_dir + 'remote.json'
    }
    return inpaths


def read_golden(input_dir):
    def to_dt(entry):
        if entry['action'] == 'add':
            started = entry['worklog']['started']
            entry['worklog']['started'] = strptime_ptl(started)
        return entry
    with open(input_dir + 'gld-remotecmds.json', 'r') as file:
        gld_rcmds = [to_dt(x) for x in json.load(file)]
    with open(input_dir + 'gld-checkedin.json', 'r') as file:
        gld_chk = json.load(file)
    return (gld_rcmds, gld_chk)
