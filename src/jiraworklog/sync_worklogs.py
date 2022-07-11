#!/usr/bin/env python3

from jiraworklog.configuration import read_conf
from jiraworklog.diff_worklogs import augm_wkls_jira, augm_wkls_checkedin, augm_wkls_local, diff_worklogs_jira, diff_worklogs_local
from jiraworklog.read_local_worklogs import read_wkls_local
from jiraworklog.read_checkedin_worklogs import read_wkls_checkedin
from jiraworklog.read_jira_worklogs import read_wkls_jira
from jiraworklog.reconcile_external import create_update_instructions
from jiraworklog.push_worklogs import push_worklogs

def sync_worklogs(jira, worklogs_path):
    conf = read_conf()
    local_worklogs = read_wkls_local(worklogs_path)
    checkedin_worklogs = read_wkls_checkedin(conf)
    remote_worklogs = read_wkls_jira(jira, conf)
    update_instrs = sync_worklogs_pure(
        local_worklogs,
        checkedin_worklogs,
        remote_worklogs
    )
    try:
        push_worklogs(jira, checkedin_worklogs, update_instrs)
    finally:
        # TODO: update checked-in worklogs on disk. This construction depends on
        # the partially updated version of `checkedin_worklogs` being available
        pass

def sync_worklogs_pure(local_worklogs, checkedin_worklogs, remote_worklogs):
    local_augwkls = augm_wkls_local(local_worklogs)
    checkedin_augwkls = augm_wkls_checkedin(checkedin_worklogs)
    remote_augwkls = augm_wkls_jira(remote_worklogs)
    diffs_local = diff_worklogs_local(local_augwkls, checkedin_augwkls)
    diffs_remote = diff_worklogs_jira(remote_augwkls, checkedin_augwkls)
    update_instrs = create_update_instructions(diffs_local, diffs_remote)
    return update_instrs
