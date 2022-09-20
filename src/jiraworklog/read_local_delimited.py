#!/usr/bin/env python3

import csv
from datetime import datetime
from functools import total_ordering
from jiraworklog.configuration import Configuration
from jiraworklog.read_local_common import (
    DurationJiraStyleError,
    InvalidRawElement,
    LeftError,
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


@total_ordering
class DelimitedInvalid(InvalidRawElement):

    def __init__(self, entry: DelimitedRow) -> None:
        self.entry = entry

    def __lt__(self, other) -> bool:
        is_lt = (
            isinstance(other, DelimitedInvalid)
            and self.entry.index < other.entry.index
        )
        return is_lt


class DelimitedInvalidTooFewElems(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = f"row {self.entry.index}: not enough entries"
        return msg


class DelimitedInvalidTooManyElems(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = f"row {self.entry.index}: too many entries"
        return msg


class DelimitedInvalidStrptime(DelimitedInvalid):

    def __init__(
        self,
        entry: DelimitedRow,
        value: str,
        col_label: str,
        fmt_str: str
    ):
        self.entry = entry
        self.value = value
        self.col_label = col_label
        self.fmt_str = fmt_str

    def err_msg(self) -> str:
        msg = (
            f"row {self.entry.index} '{self.col_label}' field: '{self.value}' "
            f"doesn't satisfy the parse format '{self.fmt_str}'"
        )
        return msg


class StrptimeError(Exception):
    pass


def read_local_delimited(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native, errors = read_native_wkls_delimited(worklogs_path, conf)
    canon_wkls = create_canon_wkls_delimited(worklogs_native, conf, errors)
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
) -> tuple[list[DelimitedRow], list[DelimitedInvalid]]:
    dialect_args = construct_dialect_args(conf)
    with smart_open(worklogs_path, mode='r', newline='') as csv_file:
        entries = []
        errors = []
        reader = csv.DictReader(csv_file, **dialect_args)
        try:
            for i, row in enumerate(reader):
                # From https://docs.python.org/3/library/csv.html: if a row has
                # more fields than fieldnames, the remaining data is put in a
                # list and stored with the fieldname specified by restkey (which
                # defaults to None). If a non-blank row has fewer fields than
                # fieldnames, the missing values are filled-in with the value of
                # restval (which defaults to None).
                delim_row = DelimitedRow(row, i)
                if None in row:
                    errors.append(DelimitedInvalidTooManyElems(delim_row))
                elif None in row.values():
                    errors.append(DelimitedInvalidTooFewElems(delim_row))
                else:
                    entries.append(delim_row)
        # See https://docs.python.org/3/library/csv.html#csv.Error
        except csv.Error as exc:
            # FIXME
            raise RuntimeError('Error parsing the CSV file') from exc
    return (entries, errors)


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


def create_canon_wkls_delimited(worklogs_native, conf, errors):
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pd = conf.parse_delimited
    cl = pd['col_labels']
    cf = pd['col_formats']
    maybe_tz = pd.get('timezone')
    parse_entry = make_parse_entry(
        parse_description=make_parse_string_delim(cl['description']),
        parse_start=make_parse_dt_delim(cl.get('start'), cf.get('start'), maybe_tz, conf),
        parse_end=make_parse_dt_delim(cl.get('end'), cf.get('end'), maybe_tz, conf),
        parse_duration=make_parse_duration_delim(cl.get('duration'), conf),
        parse_tags=make_parse_tags_delim(cl['tags'], pd.get('delimiter2'))
    )
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_entry=parse_entry,
        errors=errors
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
    maybe_tz: Optional[str],
    conf: Configuration
):
    def parse_dt_delim(delim_row: DelimitedRow, key: str):
        if not maybe_fmt_str:
            # We're assuming that the configuration file parser has ensured that
            # if `maybe_key` is non-None then `maybe_fmt_str` must also be
            # non-None
            raise RuntimeError('Internal logic error. Please file a bug report')
        # dt_str = delim_row.row[maybe_key]
        dt_str = extract_string_delim(delim_row, key)
        try:
            dt = parse_time_str(dt_str, maybe_fmt_str, maybe_tz)
        except StrptimeError:
            invalid = DelimitedInvalidStrptime(delim_row, dt_str, rev_col_map[key], maybe_fmt_str)
            raise LeftError(invalid)
        return dt
    parse_maybe_dt_delim = make_parse_field(maybe_key, parse_dt_delim)
    rev_col_map = create_rev_col_map(conf)
    return parse_maybe_dt_delim


# TODO
def make_parse_duration_delim(maybe_key, conf):
    def parse_duration_delim(delim_row: DelimitedRow, key: str):
        duration_str = extract_string_delim(delim_row, key)
        try:
            duration = parse_duration(duration_str)
        except DurationJiraStyleError as exc:
            pass
        return duration
    parse_maybe_duration = make_parse_field(maybe_key, parse_duration_delim)
    rev_col_map = create_rev_col_map(conf)
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
    try:
        dt = datetime.strptime(time_str, fmt_str)
    except Exception as exc:
        raise StrptimeError() from exc
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

def create_rev_col_map(conf: Configuration) -> dict[str, str]:
    if not conf.parse_delimited:
        raise RuntimeError('Internal logic error. Please file a bug report')
    col_labels = conf.parse_delimited['col_labels']
    # This assumes that the configuration parses has ensured that no two values
    # in `col_labels` are the same
    rev_col_map = {}
    for k, v in col_labels.items():
        if v:
            rev_col_map[v] = k
    return rev_col_map
