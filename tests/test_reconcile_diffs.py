#!/usr/bin/env python3

from copy import deepcopy
from jiraworklog.reconcile_diffs import reconcile_diffs
from tests.data_diffs import *
from tests.data_worklogs import *
from tests.jiramock import BuildCheckedin, to_addentry, to_rementry


def test_reconcile_diffs_no_changes():
    """No local or remote changes"""

    # Confirm the form of the data inputs
    chk, diffs = diffs_empty
    assert_keys(diffs['diffs_local'], ['P9992-3'])
    assert diffs['diffs_local']['P9992-3'].added == []
    assert diffs['diffs_local']['P9992-3'].removed == []
    assert_keys(diffs['diffs_remote'], ['P9992-3'])
    assert diffs['diffs_remote']['P9992-3'].added == []
    assert diffs['diffs_remote']['P9992-3'].removed == []

    # Setup
    jiraclient.clear()
    prev_chk = deepcopy(chk)
    build_chk = BuildCheckedin()

    # Process diffs and push updates
    instr = reconcile_diffs(**diffs)
    instr.push_worklogs(chk, jiraclient)

    # Check the updated version of the checked-in worklogs
    assert prev_chk == chk

    # Check the log of mocked remote server requests
    assert jiraclient.entries == []


# TODO: add test for remote-only changes


def test_reconcile_diffs_addlocal():
    """Add two local worklogs"""

    # Confirm the form of the data inputs
    chk, diffs = diffs_addlocal
    assert_keys(diffs['diffs_local'], ['P9992-3'])
    assert diffs['diffs_local']['P9992-3'].added == local_0to2['P9992-3']
    assert diffs['diffs_local']['P9992-3'].removed == []
    assert_keys(diffs['diffs_remote'], ['P9992-3'])
    assert diffs['diffs_remote']['P9992-3'].added == []
    assert diffs['diffs_remote']['P9992-3'].removed == []

    # Setup
    jiraclient.clear()
    prev_chk = deepcopy(chk)
    build_chk = BuildCheckedin()

    # Process diffs and push updates
    instr = reconcile_diffs(**diffs)
    instr.push_worklogs(chk, jiraclient)

    # Check the updated version of the checked-in worklogs
    new_wkls = build_chk.build_listchk(local_0to2['P9992-3'])
    prev_chk['P9992-3'].extend(new_wkls)
    assert prev_chk == chk

    # Check the mocked commands log that would be sent to the Jira server
    entries = to_addentry(local_0to2['P9992-3'])
    assert jiraclient.entries == entries


def test_reconcile_diffs_remlocal():
    """Add two local worklogs"""

    # Confirm the form of the data inputs
    chk, diffs = diffs_remlocal
    assert_keys(diffs['diffs_local'], ['P9992-3'])
    assert diffs['diffs_local']['P9992-3'].added == []
    assert diffs['diffs_local']['P9992-3'].removed == checkedin_1to3['P9992-3']
    assert_keys(diffs['diffs_remote'], ['P9992-3'])
    assert diffs['diffs_remote']['P9992-3'].added == []
    assert diffs['diffs_remote']['P9992-3'].removed == []

    # Setup
    jiraclient.clear()
    prev_chk = deepcopy(chk)
    build_chk = BuildCheckedin()

    # Process diffs and push updates
    instr = reconcile_diffs(**diffs)
    instr.push_worklogs(chk, jiraclient)

    # Check the updated version of the checked-in worklogs
    prev_chk['P9992-3'].remove(checkedin_1to3['P9992-3'][0])
    prev_chk['P9992-3'].remove(checkedin_1to3['P9992-3'][1])
    assert prev_chk == chk

    # Check the mocked commands log that would be sent to the Jira server
    entries = to_rementry(checkedin_1to3['P9992-3'])
    assert jiraclient.entries == entries


def test_reconcile_diffs_bothlocal():
    """Add and remove a local worklog, add a reconciled worklog"""

    # Confirm the form of the data inputs
    chk, diffs = diffs_bothlocal
    assert_keys(diffs['diffs_local'], ['P9992-3'])
    assert diffs['diffs_local']['P9992-3'].added == local_1to3['P9992-3']
    assert diffs['diffs_local']['P9992-3'].removed == checkedin_0to1['P9992-3']
    assert_keys(diffs['diffs_remote'], ['P9992-3'])
    assert diffs['diffs_remote']['P9992-3'].added == remote_2to3['P9992-3']
    assert diffs['diffs_remote']['P9992-3'].removed == []

    # Setup
    jiraclient.clear()
    prev_chk = deepcopy(chk)
    build_chk = BuildCheckedin()

    # Process diffs and push updates
    # FIXME: running this test in the REPL twice throws an error, something must be getting mutated?
    # Traceback (most recent call last):
    #   File "<string>", line 17, in __PYTHON_EL_eval
    #   File "/Users/david.pritchard/Dev/jira-worklog/tests/test_reconcile_diffs.py", line 122, in <module>
    #     instr.push_worklogs(chk, jiraclient)
    #   File "/Users/david.pritchard/Dev/jira-worklog/src/jiraworklog/update_instructions.py", line 47, in push_worklogs
    #     self.remote_remove(checkedin_wkls)
    #   File "/Users/david.pritchard/Dev/jira-worklog/src/jiraworklog/update_instructions.py", line 76, in remote_remove
    #     push_worklog_remove(checkedin_wkls, wkl)
    #   File "/Users/david.pritchard/Dev/jira-worklog/src/jiraworklog/update_instructions.py", line 115, in push_worklog_remove
    #     update_checkedin_remove(checkedin_wkls, jira_wkl)
    #   File "/Users/david.pritchard/Dev/jira-worklog/src/jiraworklog/update_instructions.py", line 91, in update_checkedin_remove
    #     checkedin_wkls[jira_wkl.issueKey].remove(jira_wkl)
    # ValueError: list.remove(x): x not in list
    instr = reconcile_diffs(**diffs)
    instr.push_worklogs(chk, jiraclient)

    # # Check the updated version of the checked-in worklogs
    c0 = remote_2to3['P9992-3'][0].to_checkedin()
    jw = build_chk.buildwkl(local_1to3['P9992-3'][0])
    c1 = WorklogJira(jw, local_1to3['P9992-3'][0].issueKey).to_checkedin()
    prev_chk['P9992-3'].append(c0)                            # added by both the local and the remote
    prev_chk['P9992-3'].append(c1)                            # added by local only
    prev_chk['P9992-3'].remove(checkedin_0to1['P9992-3'][0])  # removed by local only
    assert prev_chk == chk

    # Check the mocked commands log that would be sent to the Jira server
    entries = (to_addentry(local_1to3['P9992-3'][0:1])
               + to_rementry(checkedin_0to1['P9992-3'][0:1]))
    assert jiraclient.entries == entries
