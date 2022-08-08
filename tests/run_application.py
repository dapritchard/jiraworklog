#!/usr/bin/env python3

from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.sync_worklogs import sync_worklogs
import json
from tests.jiramock import JIRAMock


def run_application(
    args: list[str],
    jira: JIRAMock,
    checkedin_inpath: str,
    checkedin_outpath: str,
    remotecmds_outpath: str
) -> None:

    def stringify(entry):
        if entry['action'] == 'add':
            started = entry['worklog']['started']
            entry['worklog']['started'] = started.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        return entry

    parsed_args = parser.parse_args(args)
    conf = read_conf(parsed_args.config_path)
    conf.checked_in_path = checkedin_inpath

    jira, _ = sync_worklogs(jira, conf, parsed_args.file, checkedin_outpath)
    entries = [stringify(x) for x in jira.entries]
    with open(remotecmds_outpath, "w") as file:
        json.dump(obj=entries, fp=file, indent=4)
