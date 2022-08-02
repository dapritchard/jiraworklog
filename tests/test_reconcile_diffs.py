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
