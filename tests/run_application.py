#!/usr/bin/env python3

from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.confirm_updates import confirm_updates, unconditional_updates
from jiraworklog.read_checkedin_worklogs import confirm_new_checkedin, unconditional_new_checkedin
from jiraworklog.sync_worklogs import sync_worklogs
from jiraworklog.update_instructions import UpdateInstructions
from tests.jiramock import JIRAMock, init_jira
from typing import Any, Tuple


def run_application(
    args: list[str],
    checkedin_inpath: str,
    mockremote_inpath: str
) -> Tuple[JIRAMock, dict[str, Any], UpdateInstructions]:
    parsed_args = parser.parse_args(args)
    conf = read_conf(parsed_args.config_path)
    conf.checked_in_path = checkedin_inpath
    # FIXME: if we're testing an error in the checked-in worklogs file then
    # init_jira fails. Need to catch and place a dummy value for that case?
    jiramock = init_jira(mockremote_inpath)
    return sync_worklogs(jiramock, conf, parsed_args, parsed_args.file, False)
