#!/usr/bin/env python3

from copy import deepcopy
from jiraworklog.reconcile_diffs import reconcile_diffs
from tests.data_diffs import *
from tests.data_worklogs import *
from tests.jiramock import BuildCheckedin, to_addentry


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

    instr = reconcile_diffs(**diffs)
    jiraclient.clear()
    # Test `checkedin_add`
    prev_chk = deepcopy(chk)
    instr.checkedin_add(chk)
    assert chk == prev_chk
    # Test `checkedin_remove`
    prev_chk = deepcopy(chk)
    instr.checkedin_remove(chk)
    assert chk == prev_chk
    # Test `remote_add`
    prev_chk = deepcopy(chk)
    instr.remote_add(chk, jiraclient)
    assert chk == prev_chk
    assert jiraclient.entries == []
    # Test `remote_remove`
    prev_chk = deepcopy(chk)
    instr.remote_remove(chk)
    assert chk == prev_chk
    assert jiraclient.entries == []


def test_reconcile_diffs_addlocal():
    """Add two local worklogs"""

    # Confirm the form of the data inputs
    chk, diffs = diffs_addlocal
    assert_keys(diffs['diffs_local'], ['P9992-3'])
    assert diffs['diffs_local']['P9992-3'].added == local_wkls['P9992-3'][:2]
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

    new_wkls = build_chk.build_listchk(local_wkls['P9992-3'][:2])
    prev_chk['P9992-3'].extend(new_wkls)
    assert prev_chk == chk

    entries = to_addentry(local_wkls['P9992-3'][:2])
    assert jiraclient.entries == entries
