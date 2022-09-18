#!/usr/bin/env python3

import csv
from datetime import datetime
from jiraworklog.configuration import Configuration
from jiraworklog.read_local_common import (
    add_tzinfo,
    create_canon_wkls,
    make_parse_field,
    # make_maybe_parse_duration,
    # make_maybe_parse_time_str,
    make_parse_entry,
    # make_parse_tags,
    parse_duration,
    smart_open
)
from jiraworklog.worklogs import WorklogCanon
from typing import Any, Callable, Optional


class DelimitedRow:

    def __init__(
        self,
        row: dict[str, str],
        index: int
    ):
        self.row = row
        self.index = index


def read_local_delimited(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native = read_native_wkls_delimited(worklogs_path, conf)
    canon_wkls = create_canon_wkls_delimited(worklogs_native, conf)
    return canon_wkls


# Return a list with each entry a row in the CSV
#
# # Get the values provides by the CSV reader default (i.e. `excel`)
# # Note that the `quoting` attribute corresponds to `csv.QUOTE_MINIMAL`
# # https://docs.python.org/3/library/csv.html#csv.QUOTE_MINIMAL
# excel_options = {
#     x: getattr(csv.excel, x)
#     for x in dir(csv.excel)
#     if not x.startswith('_')
# }
def read_native_wkls_delimited(
    worklogs_path: str,
    conf: Configuration
# ) -> list[dict[str, str]]:
) -> list[DelimitedRow]:
    dialect_args = construct_dialect_args(conf)
    with smart_open(worklogs_path, mode='r', newline='') as csv_file:
        entries = []
        reader = csv.DictReader(csv_file, **dialect_args)
        for i, row in enumerate(reader):
            # TODO: check that we have the right number of columns
            # https://docs.python.org/3/library/csv.html
            # If a row has more fields than fieldnames, the remaining data is
            # put in a list and stored with the fieldname specified by restkey
            # (which defaults to None). If a non-blank row has fewer fields than
            # fieldnames, the missing values are filled-in with the value of
            # restval (which defaults to None).
            # TODO: what circumstances, if any, will cause an exception?
            entries.append(DelimitedRow(row, i))
    return entries


def construct_dialect_args(conf):
    # Note that the `escapechar` option has a valid value of `None`. In general
    # the configuration schema allows for values of `None` to have the same
    # meaning as omitting the field, which for the fields in `dialect`
    # correspond to using the default value. Since `None` is the default for the
    # `escapechar` option the semantics are aligned, but if that were to change
    # we would need to change the use of `None` to correspond to the default
    # value (for that field, at least).
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    dialect_args = {'strict': True}
    dialect = conf.parse_delimited.get('dialect')
    if dialect:
        # We are assuming that 'strict' is not a valid field in the
        # configuration file. If that ever changes we should remove this
        # assertion
        assert 'strict' not in dialect
        for k, v in dialect.items():
            if v:
                dialect_args[k] = v
    return dialect_args


def create_canon_wkls_delimited(worklogs_native, conf):
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pd = conf.parse_delimited
    cl = pd['col_labels']
    cf = pd['col_formats']
    maybe_tz = pd.get('timezone')
    parse_entry = make_parse_entry(
        parse_description=make_parse_string_delim(cl['description']),
        parse_start=make_parse_dt_delim(cl.get('start'), cf.get('start'), maybe_tz),
        parse_end=make_parse_dt_delim(cl.get('end'), cf.get('end'), maybe_tz),
        parse_duration=make_parse_duration_delim(cl.get('duration')),
        parse_tags=make_parse_tags_delim(cl['tags'], pd.get('delimiter2'))
    )
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_entry=parse_entry
    )
    return canon_wkls


def make_parse_string_delim(key: str) -> Callable[[DelimitedRow], str]:
# def make_parse_string_delim(key: str) -> Callable[[dict[str, str]], str]:
    # TODO: use functools?
    def parse_string(entry: DelimitedRow):
    # def parse_string(entry: dict[str, str]):
        value = extract_string_delim(entry, key)
        return value
    return parse_string


def make_parse_dt_delim(
    maybe_key: Optional[str],
    maybe_fmt_str: Optional[str],
    maybe_tz: Optional[str]
):
    def parse_dt_delim(delim_row: DelimitedRow, key: str):
        if not maybe_fmt_str:
            # We're assuming that the configuration file parser has ensured that
            # if `maybe_key` is non-None then `maybe_fmt_str` must also be
            # non-None
            raise RuntimeError('Internal logic error. Please file a bug report')
        # dt_str = delim_row.row[maybe_key]
        dt_str = extract_string_delim(delim_row, key)
        dt = parse_time_str(dt_str, maybe_fmt_str, maybe_tz)
        return dt
    parse_maybe_dt_delim = make_parse_field(maybe_key, parse_dt_delim)
    return parse_maybe_dt_delim


# TODO
def make_parse_duration_delim(maybe_key):
    def parse_duration_delim(delim_row: DelimitedRow, key: str):
        duration_str = extract_string_delim(delim_row, key)
        duration = parse_duration(duration_str)
        return duration
    parse_maybe_duration = make_parse_field(maybe_key, parse_duration_delim)
    return parse_maybe_duration


# TODO
def make_parse_tags_delim(key, maybe_delimiter2: Optional[str]):
    def parse_tags_delim(entry):
        tags_string = extract_string_delim(entry, key)
        if maybe_delimiter2:
            tags = set(tags_string.split(maybe_delimiter2))
        else:
            tags = set([tags_string])
        return tags
    return parse_tags_delim


def extract_string_delim(
    entry: DelimitedRow,
    key: str
) -> str:
    value = entry.row[key]
    return value


def parse_time_str(time_str, fmt_str, tz_maybestr):
    dt = datetime.strptime(time_str, fmt_str)
    dt_aware = add_tzinfo(dt, tz_maybestr)
    return dt_aware


# def make_maybe_parse_time_delim(maybe_key, maybe_fmt_str, maybe_tz):
#     def parse_time_str(entry):
#         dt = datetime.strptime(entry[maybe_key], maybe_fmt_str)
#         dt_aware = add_tzinfo(dt, maybe_tz)
#         return dt_aware
#     if maybe_key:
#         if maybe_fmt_str:
#             return parse_time_str
#         else:
#             # We assume that if the key is given that the format string is also
#             # given and this is enforced as part of the configuration parsing
#             raise RuntimeError('Internal logic error. Please file a bug report')
#     else:
#         return lambda _: None
