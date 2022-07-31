#!/usr/bin/env python3

from copy import deepcopy
from jiraworklog.reconcile_diffs import reconcile_diffs
from tests.data_diffs import *
from tests.data_worklogs import *


def test_reconcile_diffs_no_changes():
    """Test no local or remote changes"""

    # Confirm the data inputs
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
    assert prev_chk == chk
    # Test `checkedin_remove`
    prev_chk = deepcopy(chk)
    instr.checkedin_remove(chk)
    assert prev_chk == chk
    # Test `remote_add`
    prev_chk = deepcopy(chk)
    instr.remote_add(chk, jiraclient)
    assert prev_chk == chk
    assert jiraclient.entries == []
    # Test `remote_remove`
    prev_chk = deepcopy(chk)
    instr.remote_remove(chk)
    assert prev_chk == chk
    assert jiraclient.entries == []
