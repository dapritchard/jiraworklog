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
    if parsed_args.auto_confirm:
        actions = {
            'confirm_new_checkedin': unconditional_new_checkedin,
            'confirm_updates': unconditional_updates
        }
    else:
        actions = {
            'confirm_new_checkedin': confirm_new_checkedin,
            'confirm_updates': confirm_updates
        }
    conf = read_conf(parsed_args.config_path)
    conf.checked_in_path = checkedin_inpath
    jiramock = init_jira(mockremote_inpath)
    return sync_worklogs(jiramock, conf, parsed_args, parsed_args.file, actions)
