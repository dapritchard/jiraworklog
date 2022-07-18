#!/usr/bin/env python3

import os.path
import yaml

from typing import (Any, Dict)

class Configuration:

    def __init__(self, raw: Dict[str, Any]):

        self.author = raw['author']

        self.issues_map = raw['issues_map']

        self.issue_nms = self.issues_map.values()

        self.timezone = raw.get('timezone')

        self.checked_in_path = raw.get('checked_in_path')

        self.parse_type = raw['parse_type']

        self.parse_delimited = raw.get('parse_delimited')


def read_conf():
    with open(os.path.expanduser('~/.jwconfig.yaml'), 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    return contents

# # Jira issues can be identified by either ID or by key. IDs are immutable but
# # keys can change, for example when an issue moves to another project. See
# # https://community.atlassian.com/t5/Agile-questions/Unique-Issue-ID-where-do-we-stand/qaq-p/586280?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjMyMTU0MzIzNDMxfQ%3D%3D
# #
# # In the configuration users can currently specify either.
# #
# # TODO: at some point maybe once we look up an entry by key
# def conf_jira_issue_nms(conf):
#     return conf['issues_map'].values()
