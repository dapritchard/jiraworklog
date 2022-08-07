#!/usr/bin/env python3

import json
import os
import shutil

import difflib
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogJira
from tests.jiramock import JIRAMock, JIRAWklMock
from tests.run_application import run_application

os.makedirs('tests/temp', exist_ok=True)


def assert_golden(expected_path: str, actual_path: str) -> None:
    diff = calc_diff(expected_path, actual_path)
    if len(diff) >= 1:
        msg = ''.join(diff)
        raise RuntimeError(msg)


def calc_diff(path_1: str, path_2: str):
    with open(path_1, 'r') as file_1:
        with open(path_2, 'r') as file_2:
            diff = difflib.unified_diff(
                file_1.readlines(),
                file_2.readlines(),
                fromfile=path_1,
                tofile=path_2,
            )
    return list(diff)

def test_1():
    out = exercise_system(
        config_path='tests/data/configs/config-csv.yaml',
        worklogs_path='tests/data/worklogs/worklogs.csv',
        checkedin_path='tests/data/checkedins/empty.json',
        remote_path='tests/data/checkedins/empty.json'
    )
    assert_golden('tests/data/checkedins/empty.json', 'tests/temp/checkedin.json')

def exercise_system(
    config_path: str,
    worklogs_path: str,
    checkedin_path: str,
    remote_path: str
):
    shutil.copy(src=config_path, dst='tests/temp/config.yaml')
    shutil.copy(src=worklogs_path, dst='tests/temp/worklogs.csv')
    shutil.copy(src=checkedin_path, dst='tests/temp/checkedin.json')
    jiramock = init_jira(remote_path)
    jiramock_updated = run_application(
        args=['tests/temp/worklogs.csv', '--config-path', 'tests/temp/config.yaml'],
        jira=jiramock
    )
    return jiramock_updated

def init_jira(path: str) -> JIRAMock:
    mockremote_worklogs = read_mockremote_worklogs(path)
    jiramock = JIRAMock(mockremote_worklogs)
    return jiramock

def read_mockremote_worklogs(path: str) -> dict[str, list[WorklogJira]]:
    def to_jiramock(wkl_raw: dict[str, str], issue_key: str) -> WorklogJira:
        return WorklogJira(JIRAWklMock(**wkl_raw), issue_key)
    with open(path) as file:
        worklogs_raw = json.load(file)
    jiramock_wkls = map_worklogs_key(to_jiramock, worklogs_raw)
    return jiramock_wkls
