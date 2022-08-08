#!/usr/bin/env python3

import json
import os

import difflib
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogJira
from tests.jiramock import JIRAMock, JIRAWklMock
from tests.run_application import run_application
import tempfile

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


def create_test(indir_path):
    def test():
        inpaths, outpaths, outdir_path = run_test(indir_path)
        # assert_golden(inpaths['gld-chk'], outpaths['checkedin'])
        with open(inpaths['gld-chk'], 'r') as file_expected:
            with open(outpaths['checkedin'], 'r') as file_actual:
                assert json.load(file_expected) == json.load(file_actual)
        assert_golden(inpaths['gld-rcmds'], outpaths['remotecmds'])
        os.remove(outpaths['checkedin'])
        os.remove(outpaths['remotecmds'])
        os.rmdir(outdir_path)
    return test

test_1 = create_test('tests/data/01-add-to-empty/')

def run_test(indir_path: str):
    inpaths = resolve_inpaths(indir_path)
    outdir_path, outpaths = create_outpaths()
    exercise_system(inpaths, outpaths)
    return [inpaths, outpaths, outdir_path]


def exercise_system(
    inpaths: dict[str, str],
    outpaths: dict[str, str]
) -> None:
    jiramock = init_jira(inpaths['remote'])
    run_application(
        args=[inpaths['worklogs'], '--config-path', inpaths['config']],
        jira=jiramock,
        checkedin_inpath=inpaths['checkedin'],
        checkedin_outpath=outpaths['checkedin'],
        remotecmds_outpath=outpaths['remotecmds']
    )


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


def resolve_inpaths(input_dir: str) -> dict[str, str]:
    def find_remote_path(dir_path):
        for s in os.listdir(dir_path):
            if s.startswith('worklogs.'):
                return input_dir + s
        raise RuntimeError('Unable to find worklogs file')
    inpaths = {
        'config': input_dir + 'config.yaml',
        'worklogs': find_remote_path(input_dir),
        'checkedin': input_dir + 'checkedin.json',
        'remote': input_dir + 'remote.json',
        'gld-chk': input_dir + 'gld-checkedin.json',
        'gld-rcmds': input_dir + 'gld-remotecmds.json'
    }
    return inpaths


def create_outpaths():
    outdir_path = tempfile.mkdtemp()
    outpaths = {
        'checkedin': outdir_path + '/' + 'checkedin.json',
        'remotecmds': outdir_path + '/' + 'remotecmds.json'
    }
    return [outdir_path, outpaths]
