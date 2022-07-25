#!/usr/bin/env python3

# from datetime import datetime
from jira import JIRA
from jiraworklog.configuration import read_conf
from jiraworklog.diff_worklogs import diff_worklogs, diff_local, diff_remote
from jiraworklog.read_local_worklogs import read_local_worklogs
from jiraworklog.read_checkedin_worklogs import read_checkedin_worklogs
from jiraworklog.read_remote_worklogs import read_remote_worklogs
from jiraworklog.reconcile_diffs import reconcile_diffs
from jiraworklog.update_instructions import UpdateInstrs
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira, map_jira_to_canon

def sync_worklogs(jira: JIRA, worklogs_path: str) -> None:
    conf = read_conf()
    local_wkls = read_local_worklogs(worklogs_path)
    checkedin_wkls = read_checkedin_worklogs(conf)
    remote_wkls = read_remote_worklogs(jira, conf)
    update_instrs = process_worklogs_pure(
        local_wkls,
        checkedin_wkls,
        remote_wkls
    )
    try:
        update_instrs.push_worklogs_v2(jira, checkedin_wkls)
    finally:
        # TODO: update checked-in worklogs on disk. This construction depends on
        # the partially updated version of `checkedin_worklogs` being available
        pass

def process_worklogs_pure(
    local_wkls: dict[str, list[WorklogCanon]],
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    remote_wkls: dict[str, list[WorklogJira]]
) -> UpdateInstrs:
# def process_worklogs_pure(local_worklogs, checkedin_worklogs, remote_worklogs
# ) -> list[dict[str, list[WorklogCheckedin] | TODO]]:

    # Figure out what has changed in the local and the remote views, try to
    # reconcile any "external changes" (i.e. changes that occurred in both the
    # local and the remote views that isn't in the checked-in view), and create
    # a data structure of "instructions" regarding what needs to be updated in
    # the checked-in worklogs file and the remote Jira worklogs.
    diffs_local = diff_local(local_wkls, checkedin_wkls)
    diffs_remote = diff_remote(remote_wkls, checkedin_wkls)
    update_instrs = reconcile_diffs(diffs_local, diffs_remote, remote_wkls)
    return update_instrs

# def strptime_ptl(datetime_str: str) -> datetime:
#     return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
