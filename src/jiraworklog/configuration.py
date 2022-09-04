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

    auth_type: str
    auth_token: Optional[dict[str, str]]
    auth_oath: None
    issues_map: dict[str, str]
    issue_nms: list[str]
    checked_in_path: Optional[str]  # TODO: try to convert this to timezone here
    parse_type: str
    parse_delimited: Optional[dict[str, Any]]
    parse_excel: None

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
        self.parse_type = 'delimited' # TODO: should be an enum (and change type)
        self.parse_delimited = raw.get('parse_delimited')
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
        'jwconfig_version': {'type': 'string'},
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
            'required': False,
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


def perform_additional_checks_old(raw, validator):
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

    return tl



# There seem to be a number of approaches to constructing the error messages.
#
# 1. validator.errors prints a nested dictionary of error messages. The one
# disadvantage with this approach is that any information such as what the
# actual type is lost. See
# https://github.com/pyeve/cerberus/blob/8765b317442c002a84e556bd5d9677b868e6deb2/cerberus/base.py#L830
# for how the errors are created (self.error_handler is
# errors.BasicErrorHandler)
#
# 2. validator.document_error_tree
#
# 2. validator._errors gives you a flat version of t
#


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

def construct_conferr_msg_old(validator: Validator) -> list[str]:
    def create_wrongtype(obj):
        if type(obj) is list:
            return 'a sequence'
        elif type(obj) is dict:
            return 'a mapping'
        elif type(obj) is int:
            return 'an integer'
        elif type(obj) is float:
            return 'a float'
        elif type(obj) is str:
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
    if len(validator._errors) != len(msgs):
        raise ConfigParseError('Internal logic error. Please file a bug report', validator)
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
