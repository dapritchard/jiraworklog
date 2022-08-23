#!/usr/bin/env python3

# from datetime import datetime
import argparse
from jira import JIRA
from jiraworklog.configuration import Configuration
from jiraworklog.confirm_updates import confirm_updates
from jiraworklog.diff_worklogs import diff_local, diff_remote
from jiraworklog.read_local_worklogs import read_local_worklogs
from jiraworklog.read_checkedin_worklogs import read_checkedin_worklogs
from jiraworklog.read_remote_worklogs import read_remote_worklogs
from jiraworklog.reconcile_diffs import reconcile_diffs
from jiraworklog.update_instructions import UpdateInstructions
from jiraworklog.utils import map_worklogs
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira
import json
from typing import Any, Callable, Tuple, TypeVar

JiraSubcl = TypeVar('JiraSubcl', bound='JIRA')


# TODO: we want to be able to read from stdin also
def sync_worklogs(
    jira: JiraSubcl,
    conf: Configuration,
    cmdline_args: argparse.Namespace,
    worklogs_path: str,
    actions: dict[str, Callable[..., Any]],
    write_checkedin: bool = False
) -> Tuple[JiraSubcl, dict[str, Any], UpdateInstructions]:
    local_wkls = read_local_worklogs(worklogs_path, conf)
    checkedin_wkls = read_checkedin_worklogs(conf, actions)
    remote_wkls = read_remote_worklogs(jira, conf)
    update_instrs = process_worklogs_pure(
        local_wkls,
        checkedin_wkls,
        remote_wkls
    )
    if not cmdline_args.auto_confirm:
        confirm_updates(update_instrs)
    try:
        if not cmdline_args.dry_run:
            update_instrs.push_worklogs(checkedin_wkls, jira)
    finally:
        checkedin_full = map_worklogs(lambda x: x.full, checkedin_wkls)
        if not cmdline_args.dry_run and write_checkedin:
            with open(conf.checked_in_path, "w") as file:
                json.dump(obj=checkedin_full, fp=file, indent=4)
    return (jira, checkedin_full, update_instrs)


def process_worklogs_pure(
    local_wkls: dict[str, list[WorklogCanon]],
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    remote_wkls: dict[str, list[WorklogJira]]
) -> UpdateInstructions:

    # Figure out what has changed in the local and the remote views, try to
    # reconcile any "external changes" (i.e. changes that occurred in both the
    # local and the remote views that isn't in the checked-in view), and create
    # a data structure of "instructions" regarding what needs to be updated in
    # the checked-in worklogs file and the remote Jira worklogs.
    diffs_local = diff_local(local_wkls, checkedin_wkls)
    diffs_remote = diff_remote(remote_wkls, checkedin_wkls)
    update_instrs = reconcile_diffs(diffs_local, diffs_remote, remote_wkls)
    return update_instrs
