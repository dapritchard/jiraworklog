#!/usr/bin/env python3

# from jira import JIRA
from jiraworklog.auth_jira import auth_jira
from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.sync_worklogs import sync_worklogs

parsed_args = parser.parse_args()
conf = read_conf(parsed_args.config_path)
jira = auth_jira(conf)
sync_worklogs(jira, conf, parsed_args.file, conf.checked_in_path)
