#!/usr/bin/env python3

import json
import os.path

def read_checkedin_worklogs(conf):
    if 'checked_in_path' in conf and not conf['checked_in_path'] is None:
        is_default_path = False
        raw_path = conf['checked_in_path']
        checkedin_path = os.path.expanduser(raw_path)
    else:
        is_default_path = True
        raw_path = ''
        checkedin_path = os.path.expanduser(
            '~/.config/jira-worklog/checked-in-worklogs.json'
        )
    try:
        with open(checkedin_path) as checkedin_file:
            # TODO: validate contents
            worklogs = json.load(checkedin_file)
    except:
        # TODO: query user whether we should start a new file. For now we just
        # unconditionally do so
        worklogs = {}
    return worklogs
