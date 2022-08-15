#!/usr/bin/env python3

import os.path
from cerberus import Validator
import yaml

from typing import Any, Optional


class ConfigParseError(Exception):
    pass


class Configuration:

    author: str
    authentication: dict[str, str]
    issues_map: dict[str, str]
    issue_nms: list[str]
    timezone: Optional[str]
    # checked_in_path: Optional[]  # TODO: try to convert this to timezone here
    # checked_in_path: Optional[] # TODO
    # parse_type: # TODO: this should be an enum
    # parse_delimited: # TODO: this should be an optional?
    parse_excel: Optional[dict[str, str]]

    def __init__(self, raw: dict[str, Any]):

        schema = {
            'author': {'type': 'string'},
            'authentication': {
                'type': 'dict',
                'schema': {
                    'server': {'type': 'string'},
                    'user': {'type': 'string'},
                    'apt_token': {'type': 'string'},
                }
            },
            'issues_map': {
                'type': 'dict',
                'keysrules': {'type': 'string'},
                'valuesrules': {'type': 'string'}
            },
            'timezone': {
                'nullable': True,
                'type': 'string'
            },
            'checked_in_path': {
                'nullable': True,
                'type': 'string'
            },
            'parse_type': {
                'type': 'string',
                'allowed': ['csv']
            },
        }
        validator = Validator(schema)
        validator.allow_unknown = True
        if not validator.validate(raw):
            raise RuntimeError('Invalid configuration file')

        self.author = raw['author']
        self.authentication = raw['authentication']
        self.issues_map = raw['issues_map']
        self.issue_nms = list(self.issues_map.values())
        self.timezone = raw.get('timezone')
        self.checked_in_path = raw.get('checked_in_path')
        self.parse_type = raw['parse_type']
        # self.parse_delimited = raw.get('parse_delimited')
        self.parse_delimited = raw['parse_delimited']
        self.parse_excel = None  # FIXME


# raw = {
#     'author': 'asdf',
#     'authentication': {'server': 'a', 'user': 'b', 'api_token': 'c'},
#     'issues_map': {'a': 'A'},
#     'timezone': 'zzz',
#     'parse_type': 'csv',
#     # 'parse_delimited': {
#     #     'col_formats': {
#     #         'duration': None,
#     #         'end': '%Y-%m-%d %H:%M',
#     #         'start': '%Y-%m-%d %H:%M'
#     #     },
#     #     'col_labels': {
#     #         'description': 'task',
#     #         'duration': None,
#     #         'end': 'end',
#     #         'start': 'start',
#     #         'tags': 'tags'
#     #     },
#     #     'delimiter2': ':'
#     # }
# }


def read_conf(path: Optional[str]) -> Configuration:
    if path is None:
        path='~/.jwconfig.yaml'
    with open(os.path.expanduser(path), 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    conf = Configuration(contents)
    return conf


# # Jira issues can be identified by either ID or by key. IDs are immutable but
# # keys can change, for example when an issue moves to another project. See
# # https://community.atlassian.com/t5/Agile-questions/Unique-Issue-ID-where-do-we-stand/qaq-p/586280?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjMyMTU0MzIzNDMxfQ%3D%3D
# #
# # In the configuration users can currently specify either.
# #
# # TODO: at some point maybe once we look up an entry by key
# def conf_jira_issue_nms(conf):
#     return conf['issues_map'].values()
