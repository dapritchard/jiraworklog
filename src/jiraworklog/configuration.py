#!/usr/bin/env python3

import os
import os.path
from cerberus import Validator
import yaml

from typing import Any, Optional


class ConfigParseError(RuntimeError):

    validator: Optional[Validator]

    def __init__(
        self,
        message: str,
        validator: Optional[Validator] = None
    ) -> None:
        self.validator = validator
        super().__init__(message)


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

        validator, satisfies_schema = validate_config(raw)
        schema_checks = (
            []
            if satisfies_schema
            else construct_conferr_msg(validator)
        )
        additional_checks = perform_additional_checks(raw, validator)
        if schema_checks or additional_checks:
            conferrmsg = create_conferrmsg(schema_checks + additional_checks)
            raise ConfigParseError(conferrmsg, validator)

        self.auth_type = 'delimited' # TODO: should be an enum
        self.auth_token = raw.get('auth_token')
        self.issues_map = raw['issues_map']
        self.issue_nms = list(self.issues_map.values())
        # self.timezone = raw.get('timezone')
        self.checked_in_path = raw.get('checked_in_path')
        # self.parse_type = raw['parse_type']
        # self.parse_delimited = raw.get('parse_delimited')
        self.parse_delimited = raw['parse_delimited'] # FIXME
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


def validate_config(raw: dict[str, Any]) -> tuple[Validator, bool]:
    schema = {
        'auth_token': {
            'nullable': True,
            'type': 'dict',
            'schema': {
                'server': {
                    'nullable': True,
                    'type': 'string'
                },
                'user': {
                    'nullable': True,
                    'type': 'string'
                },
                'api_token': {
                    'nullable': True,
                    'type': 'string'
                },
            }
        },
        'issues_map': {
            'type': 'dict',
            'keysrules': {'type': 'string'},
            'valuesrules': {'type': 'string'}
        },
        'checked_in_path': {
            'nullable': True,
            'type': 'string'
        },
        'parse_delimited': {
            'nullable': True,
            'type': 'dict',
            'schema': {
                'delimiter': {
                    'type': 'string'
                },
                'delimiter2': {
                    'nullable': True,
                    'type': 'string'
                },
                'col_labels': {
                    'type': 'dict',
                    'schema': {
                        'description': {
                            'type': 'string'
                        },
                        'start': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'end': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'duration': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'tags': {'type': 'string'}
                    }
                },
                'col_formats': {
                    'type': 'dict',
                    'schema': {
                        'start': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'end': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'duration': {
                            'nullable': True,
                            'type': 'string'
                        },
                        'timezone': {
                            'nullable': True,
                            'type': 'string'
                        }
                    }
                }
            }
        }
    }
    validator = Validator(schema, require_all=True)
    satisfies_schema = validator.validate(raw)
    return (validator, satisfies_schema)


def perform_additional_checks(raw, validator):
    etree = validator.document_error_tree
    error_msgs = []
    # if 'parse_type' not in etree:
    #     has_pdelim = raw.get('parse_delimited') is not None
    #     has_pexcel = raw.get('parse_excel') is not None
    #     if raw['parse_type'] == 'csv':
    #         if not has_pdelim:
    #             msg = (
    #                 "If 'parse_type' has value \"csv\" then the "
    #                 "'parse_delimited' field is required"
    #             )
    #             error_msgs.append(msg)
    #         if has_pexcel:
    #             msg = (
    #                 "If 'parse_type' has value \"csv\" then the "
    #                 "'parse_excel' field cannot be provided"
    #             )
    #             error_msgs.append(msg)
    #     if raw['parse_type'] == 'excel':
    #         if has_pdelim:
    #             msg = (
    #                 "If 'parse_type' has value \"excel\" then the "
    #                 "'parse_delimited' field cannot be provided"
    #             )
    #             error_msgs.append(msg)
    #         if not has_pexcel:
    #             msg = (
    #                 "If 'parse_type' has value \"excel\" then the "
    #                 "'parse_excel' field is required"
    #             )
    #             error_msgs.append(msg)
    if 'auth_token' not in etree:
        # TODO: this
        if raw['auth_token'].get('server') is None:
            envval = os.getenv('JW_SERVER')
            if envval is None:
                error_msgs.append(mkerrmsg_noenv('server', 'JW_SERVER'))
            else:
                raw['authentication']['server'] = envval
        if raw['auth_token'].get('user') is None:
            envval = os.getenv('JW_USER')
            if envval is None:
                error_msgs.append(mkerrmsg_noenv('user', 'JW_USER'))
            else:
                raw['authentication']['user'] = envval
        if raw['auth_token'].get('api_token') is None:
            envval = os.getenv('JW_API_TOKEN')
            if envval is None:
                error_msgs.append(mkerrmsg_noenv('api_token', 'JW_API_TOKEN'))
            else:
                raw['authentication']['api_token'] = envval
    return error_msgs

def construct_conferr_msg(validator: Validator) -> list[str]:
    def create_wrongtype(obj):
        if type(obj) is list:
            return 'a sequence'
        elif type(obj) is dict:
            return 'a mapping'
        elif type(obj) is int:
            return 'an integer'
        elif type(obj) is float:
            return 'a float'
        elif type(obj) is string:
            return 'a string'
        raise RuntimeError('Internal logic error. Please file a bug report')
    msgs = []
    etree = validator.document_error_tree
    # if 'author' in etree:
    #     for err in etree['author'].errors:
    #         if err.rule == 'required':
    #             msgs.append(
    #                 "The 'author' field is required but is not provided"
    #             )
    #         elif err.rule == 'type':
    #             wrongtype = create_wrongtype(err.value)
    #             msgs.append(
    #                 f"The 'author' field is required to be a string, but "
    #                 "{wrongtype} was provided"
    #             )
    #         else:
    #             raise RuntimeError('Internal logic error. Please file a bug report')
    if 'auth_token' in etree:
        for err in etree['auth_token'].errors:
            if err.rule == 'required':
                msgs.append(
                    "The 'auth_token' field is required but is not provided"
                )
            elif err.rule == 'type':
                wrongtype = create_wrongtype(err.value)
                msgs.append(
                    f"The 'auth_token' field is required to be a mapping, "
                    "but {wrongtype} was provided"
                )
            else:
                # TODO: can be finer-grained
                msgs.append(
                    "The 'auth_token' field is incorrectly specified"
                )
    if 'issues_map' in etree:
        for err in etree['issues_map'].errors:
            if err.rule == 'required':
                msgs.append(
                    "The 'issues_map' field is required but is not provided"
                )
            elif err.rule == 'type':
                wrongtype = create_wrongtype(err.value)
                msgs.append(
                    f"The 'issues_map' field is required to be a mapping, but "
                    "{wrongtype} was provided"
                )
            else:
                # TODO: can be finer-grained
                msgs.append(
                    "The 'auth_token' field is incorrectly specified"
                )
    # if 'timezone' in etree:
    #     for err in etree['timezone'].errors:
    #         if err.rule == 'type':
    #             wrongtype = create_wrongtype(err.value)
    #             msgs.append(
    #                 f"If the 'timezone' field is provided then it is required "
    #                 'to be a string, but {wrongtype} was provided'
    #             )
    #         else:
    #             raise RuntimeError('Internal logic error. Please file a bug report')
    if 'checked_in_path' in etree:
        for err in etree['checked_in_path'].errors:
            if err.rule == 'type':
                wrongtype = create_wrongtype(err.value)
                msgs.append(
                    f"If the 'checked_in_path' field is provided then it is "
                    'required to be a string, but {wrongtype} was provided'
                )
            else:
                raise RuntimeError('Internal logic error. Please file a bug report')
    if 'parse_type' in etree:
        for err in etree['parse_type'].errors:
            if err.rule == 'required':
                msgs.append(
                    "The 'parse_type' field is required but is not provided"
                )
            elif err.rule == 'type':
                wrongtype = create_wrongtype(err.value)
                msgs.append(
                    f"The 'parse_type' field is required to be a string, but "
                    "{wrongtype} was provided"
                )
            elif err.rule == 'allowed':
                msgs.append(
                    f"The 'parse_type' field is required to be one of 'csv' or "
                    "'excel', but {err.value} was provided"
                )
            else:
                raise RuntimeError('Internal logic error. Please file a bug report')
    if 'parse_delimited' in etree:
        for err in etree['parse_delimited'].errors:
            if err.rule == 'type':
                wrongtype = create_wrongtype(err.value)
                msgs.append(
                    f"The 'parse_delimited' field is required to be a mapping, "
                    "but {wrongtype} was provided"
                )
            else:
                # TODO: can be finer-grained. Remember to use existing section for timezone
                msgs.append(
                    "The 'parse_delimited' field is incorrectly specified"
                )
    return msgs



def create_conferrmsg(msgs):
    header = (
        'The configuration file format is incorrectly specified. The '
        'following issues were found:'
    )
    conferrmsg = [header]
    for i, v in enumerate(msgs, start=1):
        conferrmsg.append(f'{i}. {v}')
    return '\n'.join(conferrmsg)


def mkerrmsg_noenv(field: str, envvar: str) -> str:
    msg = (
        f"If the '{field}' field of the 'auth_token' mapping is null then "
        f"the '{envvar}' environmental variable must be set"
    )
    return msg


def read_conf(path: Optional[str]) -> Configuration:
    if path is None:
        path='~/.jwconfig.yaml'
    with open(os.path.expanduser(path), 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    conf = Configuration(contents)
    return conf


# Jira issues can be identified by either ID or by key. IDs are immutable but
# # keys can change, for example when an issue moves to another project. See
# # https://community.atlassian.com/t5/Agile-questions/Unique-Issue-ID-where-do-we-stand/qaq-p/586280?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjMyMTU0MzIzNDMxfQ%3D%3D
# #
# # In the configuration users can currently specify either.
# #
# # TODO: at some point maybe once we look up an entry by key
# def conf_jira_issue_nms(conf):
#     return conf['issues_map'].values()
