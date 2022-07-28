#!/usr/bin/env python3

from jiraworklog.diff_worklogs import (
    DiffsLocal,
    DiffsRemote,
    diff_local,
    diff_remote
)
from tests.data_worklogs import *


def assert_lbasics(obj):
    assert isinstance(obj, dict)
    assert list(obj.keys()) == ['P9992-3']
    assert isinstance(obj['P9992-3'], DiffsLocal)
    assert isinstance(obj['P9992-3'].added, list)
    assert isinstance(obj['P9992-3'].removed, list)

def test_diff_local():
    """Check that basic comparisons work"""

    # 0 local 0 checkedin
    actual = diff_local(local_0to0, checkedin_0to0)
    assert_lbasics(actual)
    assert len(actual['P9992-3'].added) == 0
    assert len(actual['P9992-3'].removed) == 0

    # 0 local 3 checkedin
    actual = diff_local(local_0to0, checkedin_wkls)
    assert_lbasics(actual)
    assert len(actual['P9992-3'].added) == 0
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']

    # 3 local 0 checkedin
    actual = diff_local(local_wkls, checkedin_0to0)
    assert_lbasics(actual)
    assert actual['P9992-3'].added == local_wkls['P9992-3']
    assert len(actual['P9992-3'].removed) == 0

    # 3 local 3 checkedin
    actual = diff_local(local_wkls, checkedin_wkls)
    assert_lbasics(actual)
    assert len(actual['P9992-3'].added) == 0
    assert len(actual['P9992-3'].removed) == 0

    # 1 local 3 checkedin
    actual = diff_local(local_0to1, checkedin_wkls)
    assert_lbasics(actual)
    assert len(actual['P9992-3'].added) == 0
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][1:]

    # 3 local 1 checkedin
    actual = diff_local(local_wkls, checkedin_2to3)
    assert_lbasics(actual)
    assert actual['P9992-3'].added == local_wkls['P9992-3'][0:2]
    assert len(actual['P9992-3'].removed) == 0
