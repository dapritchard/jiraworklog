#!/usr/bin/env python3

from jiraworklog.diff_worklogs import (
    diff_local,
    diff_remote
)
from tests.data_worklogs import *
from typing import Any


def assert_keys(obj: dict[str, Any], keys: list[str]) -> None:
    assert set(obj.keys()) == set(keys)


def test_diff_local_basic():
    """Check that basic comparisons for one issue work"""

    # 0 local 0 checkedin
    actual = diff_local(local_0to0, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []

    # 0 local 3 checkedin
    actual = diff_local(local_0to0, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']

    # 3 local 0 checkedin
    actual = diff_local(local_wkls, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3']
    assert actual['P9992-3'].removed == []

    # 3 local 3 checkedin
    actual = diff_local(local_wkls, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []

    # 1 local 3 checkedin
    actual = diff_local(local_0to1, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][1:3]

    # 3 local 1 checkedin
    actual = diff_local(local_wkls, checkedin_2to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3'][:2]
    assert actual['P9992-3'].removed == []

    # 1 added 1 removed
    actual = diff_local(local_0to2, checkedin_1to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][2:3]


def test_diff_local_twoissue():
    """Check that basic comparisons for two issues work"""

    loc = {
        'P7777-7': localtwo_wkls['P7777-7'][0:2],
        'P9992-3': localtwo_wkls['P9992-3'][0:2]
    }
    chk = {
        'P7777-7': checkedintwo_wkls['P7777-7'],
        'P9992-3': checkedintwo_wkls['P9992-3'][1:3]
    }
    actual = diff_local(loc, chk)
    assert_keys(actual, ['P7777-7', 'P9992-3'])
    assert actual['P7777-7'].added == []
    assert actual['P7777-7'].removed == checkedintwo_wkls['P7777-7'][2:3]
    assert actual['P9992-3'].added == localtwo_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedintwo_wkls['P9992-3'][2:3]
