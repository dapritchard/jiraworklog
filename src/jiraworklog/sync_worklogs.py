#!/usr/bin/env python3

from datetime import datetime
from jira import JIRA
from jiraworklog.configuration import read_conf
from jiraworklog.diff_worklogs import (
    augm_wkls_jira,
    augm_wkls_checkedin,
    augm_wkls_local,
    diff_worklogs
)
from jiraworklog.read_local_worklogs import read_local_worklogs
from jiraworklog.read_checkedin_worklogs import read_checkedin_worklogs
from jiraworklog.read_remote_worklogs import read_remote_worklogs
from jiraworklog.reconcile_external import create_update_instructions
from jiraworklog.push_worklogs import push_worklogs

def sync_worklogs(jira: JIRA, worklogs_path: str) -> None:
    conf = read_conf()
    local_worklogs = read_local_worklogs(worklogs_path)
    checkedin_worklogs = read_checkedin_worklogs(conf)
    remote_worklogs = read_remote_worklogs(jira, conf)
    checkedin_augwkls, update_instrs = process_worklogs_pure(
        local_worklogs,
        checkedin_worklogs,
        remote_worklogs
    )
    try:
        push_worklogs(jira, checkedin_augwkls, update_instrs)
    finally:
        # TODO: update checked-in worklogs on disk. This construction depends on
        # the partially updated version of `checkedin_worklogs` being available
        pass

def process_worklogs_pure(local_worklogs, checkedin_worklogs, remote_worklogs):
# def process_worklogs_pure(local_worklogs, checkedin_worklogs, remote_worklogs
# ) -> list[dict[str, list[WorklogCheckedin] | TODO]]:

    # Worklogs preprocessing
    local_augwkls = augm_wkls_local(local_worklogs)
    checkedin_augwkls = augm_wkls_checkedin(checkedin_worklogs)
    remote_augwkls = augm_wkls_jira(remote_worklogs)

    # Figure out what has changed in the local and the remote views, try to
    # reconcile any "external changes" (i.e. changes that occurred in both the
    # local and the remote views that isn't in the checked-in view), and create
    # a data structure of "instructions" regarding what needs to be updated in
    # the checked-in worklogs file and the remote Jira worklogs.
    diffs_local = diff_worklogs(local_augwkls, checkedin_augwkls)
    diffs_remote = diff_worklogs(remote_augwkls, checkedin_augwkls)
    update_instrs = create_update_instructions(diffs_local, diffs_remote)
    return [checkedin_augwkls, update_instrs]

def strptime_ptl(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
