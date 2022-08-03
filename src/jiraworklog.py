#!/usr/bin/env python3

from jira import JIRA
from jiraworklog.auth_jira import auth_jira
from jiraworklog.cmdline_args import cmdline_args
from jiraworklog.configuration import read_conf
from jiraworklog.sync_worklogs import sync_worklogs

conf = read_conf()
jira = auth_jira(conf)
sync_worklogs(jira, conf, conf.checked_in_path)
