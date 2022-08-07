#!/usr/bin/env python3

from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.sync_worklogs import sync_worklogs
from tests.jiramock import JIRAMock


def run_application(
   args: list[str],
   jira: JIRAMock
) -> JIRAMock:
   parsed_args = parser.parse_args(args)
   conf = read_conf(parsed_args.config_path)
   sync_worklogs(jira, conf, parsed_args.file)
   return jira
