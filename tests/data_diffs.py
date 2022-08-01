#!/usr/bin/env python3

from copy import deepcopy
from jiraworklog.diff_worklogs import diff_local, diff_remote
import tests.data_worklogs as dw
from tests.utils import assert_keys


def create_diffs(local_wkls, checkedin_wkls, remote_wkls):
    diffs = {
        'diffs_local': diff_local(local_wkls, checkedin_wkls),
        'diffs_remote': diff_remote(remote_wkls, checkedin_wkls),
        'remote_wkls': remote_wkls
    }
    return [deepcopy(checkedin_wkls), diffs]

diffs_empty = create_diffs(
    dw.local_wkls,
    dw.checkedin_wkls,
    dw.remote_wkls
)

diffs_addlocal = create_diffs(
    dw.local_wkls,
    dw.checkedin_2to3,
    dw.remote_2to3
)
