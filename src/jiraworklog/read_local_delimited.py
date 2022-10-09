#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
from functools import total_ordering
from jiraworklog.configuration import Configuration
from jiraworklog.read_local_common import (
    DurationJiraStyleError,
    NativeInvalidElement,
    # NativeInvalidElementSubcl,
    LeftError,
    NativeRow,
    TimeZoneMissingTZInfo,
    TimeZoneDualTZInfo,
    create_canon_wkls,
    make_add_tzinfo,
    make_parse_field,
    # make_maybe_parse_duration,
    # make_maybe_parse_time_str,
    make_parse_entry,
    # make_parse_tags,
    parse_duration,
    smart_open
)
from jiraworklog.worklogs import WorklogCanon
from typing import Any, Callable, Optional, Sequence, TypeVar

# DelimitedInvalidElementSubcl = TypeVar('DelimitedInvalidElementSubcl', bound='DelimitedInvalid')


class DelimitedRow(NativeRow):

    row: dict[str, str]
    index: int

    def __init__(
        self,
        row: dict[str, str],
        index: int
    ) -> None:
        self.row = row
        self.index = index

    def row_index(self) -> int:
        return self.index


@total_ordering
class DelimitedInvalid(NativeInvalidElement):

    entry: DelimitedRow

    def __init__(self, entry: DelimitedRow) -> None:
        self.entry = entry

    def __lt__(self, other) -> bool:
        is_lt = (
            isinstance(other, DelimitedInvalid)
            and self.row_index() < other.row_index()
        )
        return is_lt

    def row_index(self) -> int:
        return self.entry.index


class DelimitedInvalidTooFewElems(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = f"row {self.row_index()}: not enough entries"
        return msg


class DelimitedInvalidTooManyElems(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = f"row {self.row_index()}: too many entries"
        return msg


class DelimitedInvalidStrptime(DelimitedInvalid):

    entry: DelimitedRow
    value: str
    col_label: str
    fmt_str: str

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
            f"row {self.row_index()} '{self.col_label}' field: '{self.value}' "
            f"doesn't satisfy the parse format '{self.fmt_str}'"
        )
        return msg


class DelimitedInvalidDurationJiraStyle(DelimitedInvalid):

    entry: DelimitedRow

    def __init__(
        self,
        entry: DelimitedRow,
        value: str,
        col_label: str
    ) -> None:
        self.entry = entry
        self.value = value
        self.col_label = col_label

    def err_msg(self) -> str:
        msg = (
            f"row {self.row_index()} '{self.col_label}' field: '{self.value}' "
            f"doesn't satisfy the Jira-style parse format"
        )
        return msg


class DelimitedInvalidIntervalStartAfterEnd(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = (
            f"row {self.row_index()}: the start datetime wasn't after the end "
            "datetime"
        )
        return msg


class DelimitedInvalidIntervalNegativeDuration(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = f"row {self.row_index()}: the duration was negative"
        return msg


class DelimitedInvalidInconsistentStartEndDuration(DelimitedInvalid):

    def err_msg(self) -> str:
        msg = (
            f"row {self.row_index()}: the difference between the start and end "
            "time did not match the duration"
        )
        return msg


# TODO: use this for all invalid entries?
class DelimitedInvalidBasic(DelimitedInvalid):

    def __init__(self, index: int, msg: str):
        self.index = index
        self.msg = msg

    def row_index(self) -> int:
        return self.index

    def err_msg(self) -> str:
        return f"row {self.row_index()}: {self.msg}"


class DelimitedInvalidMissingTZInfo(DelimitedInvalidBasic):

    def __init__(self, index: int) -> None:
        msg = (
            'must provide either a timezone-aware datetime or a timezone '
            'specification in the configuration file'
        )
        super().__init__(index, msg)


class DelimitedInvalidDualTZInfo(DelimitedInvalidBasic):

    def __init__(self, index: int) -> None:
        msg = (
            "can't provide both a timezone-aware datetime and a timezone "
            "specification in the configuration file"
        )
        super().__init__(index, msg)


class DelimitedInvalidMultipleTagMatches(DelimitedInvalid):

    def __init__(self, entry: DelimitedRow, tag_matches: Sequence['str']) -> None:
        super().__init__(entry)
        self.tag_matches = tag_matches

    def err_msg(self) -> str:
        tag_str = "', '".join(self.tag_matches)
        msg = f"row {self.row_index()}: multiple tag matches '{tag_str}'"
        return msg


class CSVStructuralError(Exception):

    def __init__(self, worklogs_path: str) -> None:
        self.worklogs_path = worklogs_path

    def __str__(self) -> str:
        if self.worklogs_path:
            input_fragm = "'{self.worklogs_path:}'"
        else:
            input_fragm = 'standard input'
        msg = (
            f"Error attempting to parse the worklogs from {input_fragm}:\n\n"
            f"{str(self.__cause__)}"
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
def read_native_wkls_delimited(
    worklogs_path: str,
    conf: Configuration
) -> tuple[list[DelimitedRow], list[DelimitedInvalid]]:
    dialect_args = construct_dialect_args(conf)
    # FIXME: catch this and rethrow?
    with smart_open(worklogs_path, mode='r', newline='') as csv_file:
        entries = []
        errors = []
        # TODO: this can fail if the dialect_args args are invalid. Can it fail
        # for any other reaon? We whould catch this?
        reader = csv.DictReader(csv_file, **dialect_args)
        try:
            for i, row in enumerate(reader):
                # From https://docs.python.org/3/library/csv.html: if a row has
                # more fields than fieldnames, the remaining data is put in a
                # list and stored with the fieldname specified by restkey (which
                # defaults to None). If a non-blank row has fewer fields than
                # fieldnames, the missing values are filled-in with the value of
                # restval (which defaults to None).
                # TODO: these values can't be changed by the user via
                # `construct_dialect_args`, right?
                delim_row = DelimitedRow(row, i)
                if None in row:
                    errors.append(DelimitedInvalidTooManyElems(delim_row))
                elif None in row.values():
                    errors.append(DelimitedInvalidTooFewElems(delim_row))
                else:
                    entries.append(delim_row)
        # See https://docs.python.org/3/library/csv.html#csv.Error
        except csv.Error as exc:
            # TODO: understand better how an error can actually be thrown. Does
            # this effect how the error message should be presented?
            raise CSVStructuralError(worklogs_path) from exc
    return (entries, errors)


def construct_dialect_args(conf: Configuration) -> dict[str, Any]:
    # Note that the `escapechar` option has a valid value of `None`. In general
    # the configuration schema allows for values of `None` to have the same
    # meaning as omitting the field, which for the fields in `dialect`
    # correspond to using the default value. Since `None` is the default for the
    # `escapechar` option the semantics are aligned, but if that were to change
    # we would need to change the use of `None` to correspond to the default
    # value (for that field, at least).
    quoting_map = {
        'QUOTE_ALL': csv.QUOTE_ALL,
        'QUOTE_MINIMAL': csv.QUOTE_MINIMAL,
        'QUOTE_NONNUMERIC': csv.QUOTE_NONNUMERIC,
        'QUOTE_NONE': csv.QUOTE_NONE
    }
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    dialect_args = {}
    dialect_args['strict'] = True
    dialect = conf.parse_delimited.get('dialect')
    if dialect:
        # We are assuming that 'strict' is not a valid field in the
        # configuration file. If that ever changes we should remove this
        # assertion
        assert 'strict' not in dialect
        for k, v in dialect.items():
            if v:
                if k == 'quoting':
                    dialect_args[k] = quoting_map[v]
                else:
                    dialect_args[k] = v
    return dialect_args


# TODO: We use `errors: list[Any]` instead of (I think) `errors:
# list[DelimitedInvalid]` to subvert the type-checker. The issue is that
# `make_parse_entry` returns a tuple with a NativeInvalidElement when what we
# need it to return is a DelimitedInvalid. Maybe we could rework it to accept a
# NativeInvalidElementSubcl? Perhaps if the parse function inputs returned a
# pseudo-Either type with the Left returning an Optional[DelimitedInvalid]?
def create_canon_wkls_delimited(
        worklogs_native: Sequence[DelimitedRow],
        conf: Configuration,
        # errors: list[DelimitedInvalid]
        errors: list[Any]
) -> dict[str, Any]:
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pd = conf.parse_delimited
    cl = pd['col_labels']
    cf = pd['col_formats']
    maybe_tz = cf.get('timezone')
    parse_entry = make_parse_entry(
        parse_description=make_parse_string_delim(cl['description']),
        parse_start=make_parse_dt_delim(cl.get('start'), cf.get('start'), maybe_tz, conf),
        parse_end=make_parse_dt_delim(cl.get('end'), cf.get('end'), maybe_tz, conf),
        parse_duration=make_parse_duration_delim(cl.get('duration'), conf),
        parse_tags=make_parse_tags_delim(cl['tags'], cf.get('delimiter2'))
    )
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_entry=parse_entry,
        errors=errors,
        mk_start_after_end=DelimitedInvalidIntervalStartAfterEnd,
        mk_negative_duration_error=DelimitedInvalidIntervalNegativeDuration,
        mk_inconsistent_start_end_duration=DelimitedInvalidInconsistentStartEndDuration,
        mk_multiple_tag_matches=DelimitedInvalidMultipleTagMatches
    )
    return canon_wkls


def make_parse_string_delim(key: str) -> Callable[[DelimitedRow], str]:
    # TODO: use functools?
    def parse_string(entry: DelimitedRow):
        value = extract_string_delim(entry, key)
        return value
    return parse_string


# TODO: maybe_key and maybe_fmt_str are both either maybe or not. But it is
# hard to represent that in the type system. For instance, we would like to have
# `make_parse_time_str` take `maybe_tz` as an argument as well, but we can't
# convince the type-checker that it will be non-None. It would probably be
# better to make these a Maybe ProductType.
def make_parse_dt_delim(
    maybe_key: Optional[str],
    maybe_fmt_str: Optional[str],
    maybe_tz: Optional[str],
    conf: Configuration
) -> Callable[[DelimitedRow], datetime]:
    def parse_dt_delim(delim_row: DelimitedRow, key: str):
        if not maybe_fmt_str:
            # We're assuming that the configuration file parser has ensured that
            # if `maybe_key` is non-None then `maybe_fmt_str` must also be
            # non-None
            raise RuntimeError('Internal logic error. Please file a bug report')
        dt_str = extract_string_delim(delim_row, key)
        try:
            dt = parse_time_str(dt_str, maybe_fmt_str)
        except StrptimeError:
            invalid = DelimitedInvalidStrptime(delim_row, dt_str, rev_col_map[key], maybe_fmt_str)
            raise LeftError(invalid)
        except TimeZoneMissingTZInfo:
            raise LeftError(DelimitedInvalidMissingTZInfo(delim_row.row_index()))
        except TimeZoneDualTZInfo:
            raise LeftError(DelimitedInvalidDualTZInfo(delim_row.row_index()))
        return dt
    parse_time_str = make_parse_time_str(maybe_tz)
    parse_maybe_dt_delim = make_parse_field(maybe_key, parse_dt_delim)
    rev_col_map = create_rev_col_map(conf)
    return parse_maybe_dt_delim


def make_parse_duration_delim(
    maybe_key: Optional[str],
    conf: Configuration
) -> Callable[[DelimitedRow], Optional[timedelta]]:
    def parse_duration_delim(delim_row: DelimitedRow, key: str):
        duration_str = extract_string_delim(delim_row, key)
        try:
            duration = parse_duration(duration_str)
        except DurationJiraStyleError:
            invalid = DelimitedInvalidDurationJiraStyle(delim_row, duration_str, rev_col_map[key])
            raise LeftError(invalid)
        return duration
    parse_maybe_duration = make_parse_field(maybe_key, parse_duration_delim)
    rev_col_map = create_rev_col_map(conf)
    return parse_maybe_duration


def make_parse_tags_delim(
    key: str,
    maybe_delimiter2: Optional[str]
) -> Callable[[DelimitedRow], set[str]]:
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


def make_parse_time_str(maybe_tz: Optional[str]):
    def parse_time_str(time_str: str, fmt_str: str) -> datetime:
        try:
            dt = datetime.strptime(time_str, fmt_str)
        # TODO: should we use a more fine-grained exception class? Can we?
        except Exception as exc:
            raise StrptimeError() from exc
        # Note that `add_tzinfo` can throw an error but we let it bubble up
        dt_aware = add_tzinfo(dt)
        return dt_aware
    add_tzinfo = make_add_tzinfo(maybe_tz)
    return parse_time_str


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
