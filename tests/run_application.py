#!/usr/bin/env python3

from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.sync_worklogs import sync_worklogs
from jiraworklog.update_instructions import UpdateInstructions
from tests.jiramock import JIRAMock
from typing import Any, Tuple


def run_application(
    args: list[str],
    jira: JIRAMock,
    checkedin_inpath: str
) -> Tuple[JIRAMock, dict[str, Any], UpdateInstructions]:
    parsed_args = parser.parse_args(args)
    conf = read_conf(parsed_args.config_path)
    conf.checked_in_path = checkedin_inpath
    return sync_worklogs(jira, conf, parsed_args.file)
