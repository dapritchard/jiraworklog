#!/usr/bin/env python3

import os
import os.path
from cerberus import Validator
from enum import Enum
import yaml

from typing import Any, Optional

ParseType = Enum('ParseType', ['DELIMITED', 'EXCEL'])


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

    auth_type: str
    auth_token: Optional[dict[str, str]]
    auth_oath: None
    issues_map: dict[str, str]
    issue_nms: list[str]
    checked_in_path: Optional[str]  # TODO: try to convert this to timezone here
    parse_type: str
    parse_delimited: Optional[dict[str, Any]]
    parse_excel: Optional[dict[str, Any]]

    def __init__(self, raw: dict[str, Any]):

        validator, satisfies_schema = validate_config(raw)
        errors_toplevel = perform_additional_checks(validator, raw)
        if not satisfies_schema or errors_toplevel:
            conferr_msgs = construct_conferr_msg(validator)
            conferr_msgs.extend(errors_toplevel)
            raise ConfigParseError('\n'.join(conferr_msgs), validator)

        self.auth_type = 'token' # TODO: should be an enum (and change type)
        self.auth_token = raw.get('auth_token')
        self.auth_oath = None
        self.issues_map = raw['issues_map']
        self.issue_nms = list(self.issues_map.values())
        self.checked_in_path = raw.get('checked_in_path')
        self.parse_type = get_parse_type(raw)
        self.parse_delimited = raw.get('parse_delimited')
        self.parse_excel = raw.get('parse_excel')


def validate_config(raw: dict[str, Any]) -> tuple[Validator, bool]:
    schema = {
        'jwconfig_version': {'type': 'string'},
        'auth_token': {
            # 'nullable': True,
            # 'required': False,
            'type': 'dict',
            'schema': {
                'server': {
                    'nullable': True,
                    'required': False,
                    'type': 'string'
                },
                'user': {
                    'nullable': True,
                    'required': False,
                    'type': 'string'
                },
                'api_token': {
                    'nullable': True,
                    'required': False,
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
            'required': False,
            'type': 'string'
        },
        'parse_delimited': {
            'nullable': True,
            'required': False,
            'type': 'dict',
            'schema': {
                'delimiter': {
                    'type': 'string'
                },
                'delimiter2': {
                    'nullable': True,
                    'required': False,
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
                            'required': False,
                            'type': 'string'
                        },
                        'end': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        },
                        'duration': {
                            'nullable': True,
                            'required': False,
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
                            'required': False,
                            'type': 'string'
                        },
                        'end': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        },
                        'duration': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        }
                    }
                },
                'timezone': {
                    'nullable': True,
                    'required': False,
                    'type': 'string'
                }
            }
        },
        'parse_excel': {
            'nullable': True,
            'required': False,
            'type': 'dict',
            'schema': {
                'col_labels': {
                    'type': 'dict',
                    'schema': {
                        'description': {
                            'type': 'string'
                        },
                        'start': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        },
                        'end': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        },
                        'duration': {
                            'nullable': True,
                            'required': False,
                            'type': 'string'
                        },
                        'tags': {'type': 'string'}
                    }
                },
                'timezone': {
                    'nullable': True,
                    'required': False,
                    'type': 'string'
                }
            }
        }
    }
    validator = Validator(schema, require_all=True)
    satisfies_schema = validator.validate(raw)
    return (validator, satisfies_schema)



def perform_additional_checks(
    validator: Validator,
    raw: dict[str, Any]
) -> list[str]:

    # It would probably be better to embed some of the errors directly in the
    # `validator.errors` object, but for the time-being everything just gets
    # placed in a top-level object

    dt = validator.document_error_tree

    # Container for top-level error messages. All other messages get embedded in
    # the `errors` object, but that data structure lacks a place to store the
    # top-level errors without adding dictionary elements
    tl = []

    # Must have exactly one of `auth_token` or `auth_openauth`
    has_auth_token = raw.get('auth_token') is not None
    has_auth_openauth = raw.get('auth_openauth') is not None
    if not (has_auth_token or has_auth_openauth):
        tl.append("must have either 'auth_token' or 'auth_openauth")
    elif has_auth_token and has_auth_openauth:
        tl.append("cannot have both 'auth_token' and 'auth_openauth")

    # Must have exactly one of `parse_delimited` or `parse_excel`
    has_parse_delimited = raw.get('parse_delimited') is not None
    has_parse_excel = raw.get('parse_excel') is not None
    if not (has_parse_delimited or has_parse_excel):
        tl.append("must have either 'parse_delimited' or 'parse_excel")
    elif has_parse_delimited and has_parse_excel:
        tl.append("cannot have both 'parse_delimited' and 'parse_excel")

    # Perform additional checks of `raw['parse_delimited]`
    if has_parse_delimited and 'parse_delimited' not in dt:

        cl = raw['parse_delimited']['col_labels']
        cf = raw['parse_delimited']['col_formats']

        has_cl_start = cl.get('start') is not None
        has_cl_end = cl.get('end') is not None
        has_cl_duration = cl.get('duration') is not None
        has_cf_start = cf.get('start') is not None
        has_cf_end = cf.get('end') is not None
        has_cf_duration = cf.get('duration') is not None

        if has_cl_start + has_cl_end + has_cl_duration <= 1:
            msg = "must have at least two of 'start', 'end', or 'duration'"
            tl.append(msg)

        if has_cl_start and not has_cf_start:
            msg = "no formatting information provided for the 'start' column"
            tl.append(msg)

        if has_cl_end and not has_cf_end:
            msg = "no formatting information provided for the 'end' column"
            tl.append(msg)

        if has_cl_duration and not has_cf_duration:
            msg = "no formatting information provided for the 'duration' column"
            tl.append(msg)

    # TODO: ensure delimiter isn't empty (has exactly one character?)

    return tl


def construct_conferr_msg(validator: Validator) -> list[str]:
    def create_msg(errors, pad):
        msgs = []
        for k, v in errors.items():
            for w in v:
                if isinstance(w, str) or isinstance(w, int):
                    msgs.append(f"{pad}{k}: {w}")
                else:
                    sub_errors = create_msg(w, pad + indent)
                    if len(sub_errors) == 1:
                        msgs.append(f'{pad}{k}:')
                    else:
                        msgs.append(f'{pad}{k}:')
                    msgs.extend(sub_errors)
        return msgs
    indent = '  '
    return create_msg(validator.errors, '')



def create_conferrmsg(msgs):
    header = (
        'The configuration file format is incorrectly specified. The '
        'following issues were found:'
    )
    conferrmsg = [header]
    for i, v in enumerate(msgs, start=1):
        conferrmsg.append(f'{i}. {v}')
    return '\n'.join(conferrmsg)


def read_conf(path: Optional[str]) -> Configuration:
    if path is None:
        path='~/.jwconfig.yaml'
    with open(os.path.expanduser(path), 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    conf = Configuration(contents)
    return conf


def get_parse_type(raw: dict[str, Any]) -> ParseType:
    if raw.get('parse_delimited') is not None:
        return ParseType.DELIMITED
    elif raw.get('parse_excel') is not None:
        return ParseType.EXCEL
    else:
        raise RuntimeError('Internal logic error. Please file a bug report')


# Jira issues can be identified by either ID or by key. IDs are immutable but
# # keys can change, for example when an issue moves to another project. See
# # https://community.atlassian.com/t5/Agile-questions/Unique-Issue-ID-where-do-we-stand/qaq-p/586280?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjMyMTU0MzIzNDMxfQ%3D%3D
# #
# # In the configuration users can currently specify either.
# #
# # TODO: at some point maybe once we look up an entry by key
# def conf_jira_issue_nms(conf):
#     return conf['issues_map'].values()
