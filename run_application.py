#!/usr/bin/env python3

from jiraworklog.auth_jira import auth_jira
from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import Configuration, read_conf
from tests.jiramock import JIRAMock
from jiraworklog.sync_worklogs import sync_worklogs


def run_application(args, raw_conf, jira):

   parsed_args = parser.parse_args(args)

   conf = Configuration(raw_conf)

   sync_worklogs(jira, conf, conf.checked_in_path)
