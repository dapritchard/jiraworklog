#!/usr/bin/env python3

from datetime import datetime, timedelta
from jiraworklog.worklogs import WorklogCanon
import pytz
import re
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


def create_interval(
    maybe_start: Optional[datetime],
    maybe_end: Optional[datetime],
    maybe_duration: Optional[int]
) -> Interval:

    has_start = maybe_start is not None
    has_end = maybe_end is not None
    has_duration = maybe_duration is not None

    if has_start and has_end and has_duration:
        # TODO: check that all three values are consistent
        iv = Interval(maybe_start, maybe_end - maybe_start)
    elif has_start and has_end:
        iv = Interval(maybe_start, maybe_end - maybe_start)
    elif has_start and has_duration:
        raise RuntimeError('Not yet implemented: has_start and has_duration')
    elif has_end and has_duration:
        raise RuntimeError('Not yet implemented: has_end and has_duration')
    else:
        # This case should already be caught at configuration file parse time
        raise RuntimeError('Internal logic error. Please file a bug report')

    return iv


def create_canon_wkls(
        worklogs_native,
        issues_map,
        parse_description,
        parse_start,
        parse_end,
        parse_duration,
        parse_tags
    ):

    parse_interval = make_parse_interval(parse_start, parse_end, parse_duration)
    parse_rawcanon = make_parse_rawcanon(parse_description, parse_interval)
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
        entry_tags_set = set(parse_tags(entry))
        tags_intersect = global_tags_set & entry_tags_set
        n_intersect = len(tags_intersect)
        if n_intersect == 0:
            pass
        elif n_intersect == 1:
            id = issues_map[list(tags_intersect)[0]]
            raw_canon_wkl = parse_rawcanon(entry)
            worklogs[id].append(WorklogCanon(raw_canon_wkl, id))
        else:
            # TODO: let's track these and throw an error after the loop
            raise RuntimeError('More than one tag matched')

    return worklogs


def add_tzinfo(dt: datetime, tz_maybestr: str) -> datetime:

    specified_tz = pytz.timezone(tz_maybestr) if tz_maybestr else None
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


def make_parse_interval(
        parse_start,
        parse_end,
        parse_duration
) -> Callable[[dict[str, Any]], Interval]:
    def parse_interval(entry: dict[str, Any]) -> Interval:
        maybe_start = parse_start(entry)
        maybe_end = parse_end(entry)
        maybe_duration = parse_duration(entry)
        iv = create_interval(maybe_start, maybe_end, maybe_duration)
        return iv
    return parse_interval


def make_parse_rawcanon(parse_description, parse_interval):
    def parse_rawcanon(entry):
        description = parse_description(entry)
        iv = parse_interval(entry)
        start_str = fmt_time(iv.start)
        duration_str = str(int(iv.duration.total_seconds()))
        worklog = {
            'comment': description,
            'started': start_str,
            'timeSpentSeconds': duration_str
        }
        return worklog
    return parse_rawcanon


def make_parse_field(key):
    return lambda entry: entry[key]


def make_maybe_parse_time_dt(maybe_key, maybe_tz):
    if maybe_key is None:
        return lambda _: None
    else:
        return make_parse_time_dt(key, maybe_tz)


def make_maybe_parse_time_str(maybe_key, maybe_fmt_str, maybe_tz):
    if maybe_key is None:
        return lambda _: None
    else:
        return make_parse_time_str(maybe_key, maybe_fmt_str, maybe_tz)


def make_maybe_parse_duration(maybe_key):
    if maybe_key is None:
        return lambda _: None
    else:
        return make_parse_duration(maybe_key)


def make_parse_time_dt(key, tz_maybestr):
    def parse_time_dt(entry):
        dt = entry[key]
        dt_aware = add_tzinfo(dt, tz_maybestr)
        return dt_aware
    return parse_time_dt


def make_parse_time_str(key, fmt_str, tz_maybestr):
    def parse_time_str(entry):
        dt = datetime.strptime(entry[key], fmt_str)
        dt_aware = add_tzinfo(dt, tz_maybestr)
        return dt_aware
    return parse_time_str


# def make_parse_duration(key):
def make_parse_duration(key):

    def chomp(duration_str, re_str, unit_secs):
        match = re.match(re_str, duration_str)
        if match:
            count = match.group(2)
            n_secs = int(count) * unit_secs
            new_str = duration_str[len(match.group(0)):]
            return (new_str, n_secs)
        else:
            return (duration_str, 0)

    def parse_duration(entry) -> int:

        params = [
            (r'(\s*)?(\d+)w', 604800),
            (r'(\s*)?(\d+)d',  86400),
            (r'(\s*)?(\d+)h',   3600),
            (r'(\s*)?(\d+)m',     60),
            (r'(\s*)?(\d+)s',      1)
        ]

        total_secs = 0
        duration_str = entry[key]
        for re_str, unit_secs in params:
            duration_str, n_secs = chomp(duration_str, re_str, unit_secs)
            total_secs += n_secs

        if duration_str.lstrip():
            raise RuntimeError(f"Invalid duration entry format: '{entry[key]}'")
        elif total_secs < 60:
            raise RuntimeError(f"Duration entry < 60 seconds: '{entry[key]}'")
        else:
            return total_secs

    return parse_duration


def make_parse_tags(tags_key: str, maybe_delimiter2: Optional[str]): # TODO: return type
    if maybe_delimiter2 is None:
        return lambda entry: set(entry[tags_key])
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
