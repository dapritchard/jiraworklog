#!/usr/bin/env python3

import contextlib
from datetime import datetime, timedelta
from jiraworklog.worklogs import WorklogCanon
import pytz
import re
import sys
from typing import Any, Callable, Optional


class Interval:

    start: datetime
    duration: timedelta

    def __init__(
        self,
        start: datetime,
        duration: timedelta
    ) -> None:
        self.start = start
        self.duration = duration


class RawWorklogParseEntryError(RuntimeError):

    def __init__(self, errors) -> None:
        self.errors = sorted(errors)

    def __str__(self) -> str:
        msg = []
        # FIXME: typing
        for e in self.errors:
            msg.append(e.err_msg())
        return '\n'.join(msg)


class InvalidRawElement:

    def __init__(self):
        pass

    # TODO: make this an abstract class/method
    def err_msg(self) -> str:
        return ''


class DurationJiraStyleError(Exception):
    pass


# A hacky analogue to an Either Left
class LeftError(RuntimeError):

    def __init__(self, payload: Any) -> None:
        self.payload = payload
        # TODO: Update message to say that this is expected to always be caught
        super().__init__('Internal logic error. Please file a bug report')


# class TZInfoError(RuntimeError):



def create_interval(
    maybe_start: Optional[datetime],
    maybe_end: Optional[datetime],
    maybe_duration: Optional[timedelta]
) -> Interval:

    if maybe_start and maybe_end and maybe_duration:
        iv = Interval(maybe_start, maybe_end - maybe_start)
        diff = iv.duration.total_seconds() - maybe_duration.total_seconds()
        if abs(diff) > 1.0:
            raise RuntimeError('Inconsistent start, end, and duration entries.')
    elif maybe_start and maybe_end:
        iv = Interval(maybe_start, maybe_end - maybe_start)
    elif maybe_start and maybe_duration:
        iv = Interval(maybe_start, maybe_duration)
    elif maybe_end and maybe_duration:
        iv = Interval(maybe_end - maybe_duration, maybe_duration)
    else:
        # This case should already be caught at configuration file parse time
        raise RuntimeError('Internal logic error. Please file a bug report')

    return iv


def create_canon_wkls(
        worklogs_native,
        issues_map,
        parse_entry,
        errors
    ):

    # parse_interval = make_parse_interval(parse_start, parse_end, parse_duration)
    # parse_rawcanon = make_parse_rawcanon(parse_description, parse_interval)
    global_tags_set = set(issues_map.keys())

    # Ensure that all issues have an entry in the dict, even those that don't
    # get any values mapped to them
    #
    # Note that there can be multiple local tags that map to the same issue key,
    # but that is okay since they will just overwrite an existing entry with the
    # same value
    worklogs = {}
    for nm in issues_map.values():
        worklogs[nm] = []

    for entry in worklogs_native:

        # NOTE: In the event of a parse error in the description or tags we
        # could improve this a little further by checking for errors in the
        # calculation of the Interval before giving up
        parsed_entry, entry_errors = parse_entry(entry)
        if entry_errors:
            errors.extend(entry_errors)
            continue
        else:
            entry_tags_set = set(parsed_entry['tags'])
            tags_intersect = global_tags_set & entry_tags_set
            n_intersect = len(tags_intersect)
            if n_intersect == 0:
                pass
            elif n_intersect == 1:
                id = issues_map[list(tags_intersect)[0]]
                raw_canon_wkl = create_rawcanon(parsed_entry)
                worklogs[id].append(WorklogCanon(raw_canon_wkl, id))
            else:
                # TODO: let's track these and throw an error after the loop
                raise RuntimeError('More than one tag matched')

    if errors:
        raise RawWorklogParseEntryError(errors)

    return worklogs


def make_parse_entry(
    parse_description,
    parse_start,
    parse_end,
    parse_duration,
    parse_tags
):
    def parse_entry(entry):
        parsed_entry = {}
        entry_errors = []
        try:
            parsed_entry['description'] = parse_description(entry)
        except LeftError as exc:
            entry_errors.append(exc.payload)
        try:
            parsed_entry['start'] = parse_start(entry)
        except LeftError as exc:
            entry_errors.append(exc.payload)
        try:
            parsed_entry['end'] = parse_end(entry)
        except LeftError as exc:
            entry_errors.append(exc.payload)
        try:
            parsed_entry['duration'] = parse_duration(entry)
        except LeftError as exc:
            entry_errors.append(exc.payload)
        try:
            parsed_entry['tags'] = parse_tags(entry)
        except LeftError as exc:
            entry_errors.append(exc.payload)
        return (parsed_entry, entry_errors)
    return parse_entry


def add_tzinfo(dt: datetime, maybe_tz: Optional[str]) -> datetime:

    specified_tz = pytz.timezone(maybe_tz) if maybe_tz else None
    has_tz = not check_tz_naive(dt)

    # Case: didn't specify the timezone and the parsed datetime isn't
    # timezone-aware
    if specified_tz is None and not has_tz:
        # TODO: better error type / message
        raise RuntimeError('TODO')
    # Case: didn't specify the timezone and the parsed datetime is
    # timezone-aware
    if specified_tz is None and has_tz:
        dt_aware = dt
    # Case: specified the timezone and the parsed datetime isn't
    # timezone-aware
    if specified_tz is not None and not has_tz:
        # TODO: have to add time zone
        dt_aware = specified_tz.localize(dt)
    # Case: specified the timezone and the parsed datetime is timezone-aware
    else:
        # TODO: better error type / message
        raise RuntimeError('TODO')
    return dt_aware


# def make_parse_interval(
#         parse_start,
#         parse_end,
#         parse_duration
# ) -> Callable[[dict[str, Any]], Interval]:
#     def parse_interval(entry: dict[str, Any]) -> Interval:
#         maybe_start = parse_start(entry)
#         maybe_end = parse_end(entry)
#         maybe_duration = parse_duration(entry)
#         iv = create_interval(maybe_start, maybe_end, maybe_duration)
#         return iv
#     return parse_interval


def create_rawcanon(entry: dict[str, Any]):
    iv = create_interval(entry['start'], entry['end'], entry['duration'])
    start_str = fmt_time(iv.start)
    duration_str = str(int(iv.duration.total_seconds()))
    worklog = {
        'comment': entry['description'],
        'started': start_str,
        'timeSpentSeconds': duration_str
    }
    return worklog


# def make_parse_rawcanon(parse_description, parse_interval):
#     def parse_rawcanon(entry):
#         description = parse_description(entry)
#         iv = parse_interval(entry)
#         start_str = fmt_time(iv.start)
#         duration_str = str(int(iv.duration.total_seconds()))
#         worklog = {
#             'comment': description,
#             'started': start_str,
#             'timeSpentSeconds': duration_str
#         }
#         return worklog
#     return parse_rawcanon


# def make_parse_field(key):
#     return lambda entry: entry[key]


def make_parse_field(
    maybe_key: Optional[str],
    parse_value
):
    def parse_field(entry):
        if maybe_key:
            return parse_value(entry, maybe_key)
        else:
            return None
    return parse_field


# def make_maybe_parse_time_dt(maybe_key, maybe_tz):
#     if maybe_key is None:
#         return lambda _: None
#     else:
#         return make_parse_time_dt(maybe_key, maybe_tz)

# TODO: which functions in this module are unused anywhere?


def make_maybe_parse_time_str(maybe_key, maybe_fmt_str, maybe_tz):
    if maybe_key is None:
        return lambda _: None
    else:
        return make_parse_time_str(maybe_key, maybe_fmt_str, maybe_tz)


def make_maybe_parse_duration(maybe_key):
    if maybe_key is None:
        return lambda _: None
    else:
        return make_parse_duration


# def make_parse_time_dt(key, maybe_tz):
#     def parse_time_dt(entry):
#         dt = entry[key]
#         dt_aware = add_tzinfo(dt, maybe_tz)
#         return dt_aware
#     return parse_time_dt


def make_parse_time_str(key, fmt_str, maybe_tz):
    def parse_time_str(entry):
        dt = datetime.strptime(entry[key], fmt_str)
        dt_aware = add_tzinfo(dt, maybe_tz)
        return dt_aware
    return parse_time_str


def parse_duration(duration_str: str):

    def chomp(duration_str, re_str, unit_secs):
        match = re.match(re_str, duration_str)
        if match:
            count = match.group(2)
            n_secs = int(count) * unit_secs
            new_str = duration_str[len(match.group(0)):]
            return (new_str, n_secs)
        else:
            return (duration_str, 0)

    params = [
        (r'(\s*)?(\d+)w', 604800),  # seconds in a week:   60 * 60 * 24 * 7
        (r'(\s*)?(\d+)d',  86400),  # seconds in a day:    60 * 60 * 24
        (r'(\s*)?(\d+)h',   3600),  # seconds in an hour:  60 * 60
        (r'(\s*)?(\d+)m',     60),  # seconds in a minute: 60
        (r'(\s*)?(\d+)s',      1)
    ]

    total_secs = 0
    for re_str, unit_secs in params:
        duration_str, n_secs = chomp(duration_str, re_str, unit_secs)
        total_secs += n_secs

    if duration_str.lstrip():
        raise DurationJiraStyleError()
    else:
        duration = timedelta(seconds=total_secs)

    return duration


def make_parse_duration(key):
    return lambda entry: parse_duration(entry[key])


def make_parse_tags(tags_key: str, maybe_delimiter2: Optional[str]): # TODO: return type
    if maybe_delimiter2 is None:
        return lambda entry: set([entry[tags_key]])
    else:
        return lambda entry: set(entry[tags_key].split(maybe_delimiter2))


def fmt_time(dt: datetime) -> str:
    time_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return micro_to_milli(time_str)


# https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
def check_tz_naive(dt: datetime) -> bool:
    return dt.tzinfo == None or dt.tzinfo.utcoffset(dt) == None


def micro_to_milli(time_str: str) -> str:
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3})\d{3}(-\d{4})'
    out = re.sub(pattern, "\\1\\2", time_str)
    return out


# Adapted from https://stackoverflow.com/a/17603000/5518304
@contextlib.contextmanager
def smart_open(path, *args, **kargs):
    if path:
        fh = open(path, *args, **kargs)
    else:
        fh = sys.stdin
    try:
        yield fh
    finally:
        if fh is not sys.stdin:
            fh.close()
