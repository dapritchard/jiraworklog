#!/usr/bin/env python3

import json
from jiraworklog.configuration import Configuration
# from jiraworklog.diff_worklogs import map_worklogs
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogCheckedin
import os.path
from typing import Any

def read_checkedin_worklogs(
    conf: Configuration
) -> dict[str, list[WorklogCheckedin]]:
    if conf.checked_in_path is None:
        is_default_path = True
        raw_path = ''
        checkedin_path = os.path.expanduser(
            '~/.config/jira-worklog/checked-in-worklogs.json'
        )
    else:
        is_default_path = False
        raw_path = conf.checked_in_path
        checkedin_path = os.path.expanduser(raw_path)
    try:
        with open(checkedin_path) as checkedin_file:
            # TODO: validate contents
            worklogs_raw = json.load(checkedin_file)
    except:
        # TODO: query user whether we should start a new file. For now we just
        # unconditionally do so
        worklogs_raw = {}
    align_checkedin_with_conf(worklogs_raw, conf)
    worklogs = map_worklogs_key(WorklogCheckedin, worklogs_raw)
    return worklogs

def align_checkedin_with_conf(
    worklogs: dict[str, Any],
    conf: Configuration
) -> dict[str, Any]:
    conf_nms = set(conf.issue_nms)
    checkedin_nms = set(worklogs.keys())
    added_nms = conf_nms - checkedin_nms
    removed_nms = checkedin_nms - conf_nms
    for nm in added_nms:
        worklogs[nm] = []
    if len(removed_nms) >= 1:
        # TODO: query user before removing
        for nm in removed_nms:
            del worklogs[nm]
    return worklogs
