#!/usr/bin/env python3

from jiraworklog.diff_worklogs import (
    diff_local,
    diff_remote
)
from tests.data_worklogs import *
from tests.utils import assert_keys


def test_diff_local_basic():
    """Basic comparisons for one issue"""

    # 0 local 0 checkedin
    actual = diff_local(local_0to0, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []
    # 0 remote 0 checkedin
    actual = diff_remote(remote_0to0, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []

    # 0 local 3 checkedin
    actual = diff_local(local_0to0, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']
    # 0 remote 3 checkedin
    actual = diff_remote(remote_0to0, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']

    # 3 local 0 checkedin
    actual = diff_local(local_wkls, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3']
    assert actual['P9992-3'].removed == []
    # 3 remote 0 checkedin
    actual = diff_remote(remote_wkls, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == remote_wkls['P9992-3']
    assert actual['P9992-3'].removed == []

    # 3 local 3 checkedin
    actual = diff_local(local_wkls, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []
    # 3 remote 3 checkedin
    actual = diff_remote(remote_wkls, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []

    # 1 local 3 checkedin
    actual = diff_local(local_0to1, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][1:3]
    # 1 remote 3 checkedin
    actual = diff_remote(remote_0to1, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][1:3]

    # 3 local 1 checkedin
    actual = diff_local(local_wkls, checkedin_2to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3'][:2]
    assert actual['P9992-3'].removed == []
    # 3 remote 1 checkedin
    actual = diff_remote(remote_wkls, checkedin_2to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == remote_wkls['P9992-3'][:2]
    assert actual['P9992-3'].removed == []

    # 1 added 1 removed
    actual = diff_local(local_0to2, checkedin_1to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][2:3]
    # 1 added 1 removed
    actual = diff_remote(remote_0to2, checkedin_1to3)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == remote_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3'][2:3]


def test_diff_local_twoissue():
    """Basic comparisons for two issues"""

    loc = {
        'P7777-7': localtwo_wkls['P7777-7'][0:2],
        'P9992-3': localtwo_wkls['P9992-3'][0:2]
    }
    chk = {
        'P7777-7': checkedintwo_wkls['P7777-7'],
        'P9992-3': checkedintwo_wkls['P9992-3'][1:3]
    }
    rem = {
        'P7777-7': remotetwo_wkls['P7777-7'][0:2],
        'P9992-3': remotetwo_wkls['P9992-3'][0:2]
    }

    # Local worklogs two issues
    actual = diff_local(loc, chk)
    assert_keys(actual, ['P7777-7', 'P9992-3'])
    assert actual['P7777-7'].added == []
    assert actual['P7777-7'].removed == checkedintwo_wkls['P7777-7'][2:3]
    assert actual['P9992-3'].added == localtwo_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedintwo_wkls['P9992-3'][2:3]

    # Remote worklogs two issues
    actual = diff_remote(rem, chk)
    assert_keys(actual, ['P7777-7', 'P9992-3'])
    assert actual['P7777-7'].added == []
    assert actual['P7777-7'].removed == checkedintwo_wkls['P7777-7'][2:3]
    assert actual['P9992-3'].added == remotetwo_wkls['P9992-3'][0:1]
    assert actual['P9992-3'].removed == checkedintwo_wkls['P9992-3'][2:3]


def test_diff_local_dups():
    """Comparisons for one issue with duplicates"""

    # 6 local 6 checkedin
    actual = diff_local(localdup_wkls, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []
    # 6 remote 6 checkedin
    actual = diff_remote(remotedup_wkls, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == []

    # 3 local 6 checkedin
    actual = diff_local(local_wkls, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']
    # 3 remote 6 checkedin
    actual = diff_remote(remote_wkls, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedin_wkls['P9992-3']

    # 6 local 3 checkedin
    actual = diff_local(localdup_wkls, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == local_wkls['P9992-3']
    assert actual['P9992-3'].removed == []
    # 6 remote 3 checkedin
    actual = diff_remote(remotedup_wkls, checkedin_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == remote_wkls['P9992-3']
    assert actual['P9992-3'].removed == []

    # 0 local 6 checkedin
    actual = diff_local(local_0to0, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedindup_wkls['P9992-3']
    # 0 remote 3 checkedin
    actual = diff_remote(remote_0to0, checkedindup_wkls)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == []
    assert actual['P9992-3'].removed == checkedindup_wkls['P9992-3']

    # 6 local 0 checkedin
    actual = diff_local(localdup_wkls, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == localdup_wkls['P9992-3']
    assert actual['P9992-3'].removed == []
    # 6 remote 0 checkedin
    actual = diff_remote(remotedup_wkls, checkedin_0to0)
    assert_keys(actual, ['P9992-3'])
    assert actual['P9992-3'].added == localdup_wkls['P9992-3']
    assert actual['P9992-3'].removed == []
