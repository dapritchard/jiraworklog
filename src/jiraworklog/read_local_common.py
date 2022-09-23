#!/usr/bin/env python3

from abc import ABC, abstractmethod
import contextlib
from datetime import datetime, timedelta
from functools import total_ordering
from jiraworklog.worklogs import WorklogCanon
import pytz
import re
import sys
from typing import Any, Callable, Optional, Sequence, TypeVar

NativeRowSubcl = TypeVar('NativeRowSubcl', bound='NativeRow')


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


class NativeRow(ABC):

    @abstractmethod
    def row_index(self) -> int:
        pass


@total_ordering
class NativeInvalidElement(ABC):
    """Abstract base class used to record a single parsing issue that was found
    while parsing the raw worklogs.
    """

    def __lt__(self, other) -> bool:
        is_lt = (
            isinstance(other, NativeInvalidElement)
            and self.row_index() < other.row_index()
        )
        return is_lt

    @abstractmethod
    def row_index(self) -> int:
        pass

    @abstractmethod
    def err_msg(self) -> str:
        pass


class NativeInvalidBasic(NativeInvalidElement):

    def __init__(self, index: int, msg: str):
        self.index = index
        self.msg = msg

    def row_index(self) -> int:
        return self.index

    def err_msg(self) -> str:
        return f"row {self.row_index()}: {self.msg}"


class NativeInvalidMultipleTagMatches(NativeInvalidElement):

    def __init__(self, index: int, tag_matches: list['str']) -> None:
        self.index = index
        self.tag_matches = tag_matches

    def row_index(self) -> int:
        return self.index

    def err_msg(self) -> str:
        tag_str = "', '".join(self.tag_matches)
        msg = f"row {self.row_index()}: multiple tag matches '{tag_str}'"
        return msg


class NativeWorklogParseEntryError(RuntimeError):
    """Class used to throw an error if any parsing issues were found while
    parsing the raw worklogs.
    """

    def __init__(self, errors: list[NativeInvalidElement]) -> None:
        self.errors = sorted(errors)

    def __str__(self) -> str:
        msg = []
        for e in self.errors:
            msg.append(e.err_msg())
        return '\n'.join(msg)


def make_append_invalid_elem(msg: str):
    def append_invalid_elem(
        _,
        errors: list[NativeInvalidElement],
        entry: NativeRow
    ) -> None:
        errors.append(NativeInvalidBasic(entry.row_index(), msg))
    return append_invalid_elem


class IntervalParseError(Exception):

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

    def append_invalid_elem(
        self,
        errors: list[NativeInvalidElement],
        entry: NativeRow
    ) -> None:
        errors.append(NativeInvalidBasic(entry.row_index(), self.msg))


class StartAfterEndError(IntervalParseError):

    def __init__(self):
        msg = 'the start datetime wasn\'t after the end datetime'
        super().__init__(msg)


class NegativeDurationError(IntervalParseError):

    def __init__(self):
        msg = 'the duration was negative'
        super().__init__(msg)


class InconsistentStartEndDurationError(IntervalParseError):

    def __init__(self):
        msg = (
            'the difference between the start and end time did not '
            'match the duration'
        )
        super().__init__(msg)


class DurationJiraStyleError(Exception):
    pass


class TimeZoneParseError(Exception):

    def __init__(self, tz: str):
        self.tz = tz

    # TODO: provide command-line option to pretty-print the available timezones?
    #
    #    pytz.common_timezones
    #    pytz.all_timezones
    def __str__(self):
        msg = f"unknown timezone '{self.tz}'\n"
        return msg


# A hacky analogue to an Either Left
class LeftError(Exception):

    def __init__(self, payload: Any) -> None:
        self.payload = payload
        # TODO: Update message to say that this is expected to always be caught
        super().__init__('Internal logic error. Please file a bug report')


# class TZInfoError(RuntimeError):



def create_canon_wkls(
        worklogs_native: Sequence[NativeRow],
        issues_map: dict[str, str],
        parse_entry: Callable[[NativeRowSubcl], tuple[dict[str, Any], list[NativeInvalidElement]]],
        errors: list[NativeInvalidElement]
    ) -> dict[str, Any]:

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
        # calculation of the Interval before giving up. But would we have to
        # know which elements we're supposed to have though? Is it possible to
        # have a parse error in the description or tags?
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
                try:
                    raw_canon_wkl = create_rawcanon(parsed_entry)
                except IntervalParseError as exc:
                    exc.append_invalid_elem(errors, entry)
                else:
                    worklogs[id].append(WorklogCanon(raw_canon_wkl, id))
            else:
                index = entry.row_index()
                tag_matches = sorted(list(tags_intersect))
                invalid = NativeInvalidMultipleTagMatches(index, tag_matches)
                errors.append(invalid)

    if errors:
        raise NativeWorklogParseEntryError(errors)

    return worklogs


def make_parse_entry(
    parse_description: Callable[[NativeRowSubcl], str],
    parse_start: Callable[[NativeRowSubcl], Optional[datetime]],
    parse_end: Callable[[NativeRowSubcl], Optional[datetime]],
    parse_duration: Callable[[NativeRowSubcl], Optional[timedelta]],
    parse_tags: Callable[[NativeRowSubcl], set[str]]
) -> Callable[[NativeRowSubcl], tuple[dict[str, Any], list[NativeInvalidElement]]]:
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


def create_interval(
    maybe_start: Optional[datetime],
    maybe_end: Optional[datetime],
    maybe_duration: Optional[timedelta]
) -> Interval:

    def calc_duration(start, end):
        startend_diff = end - start
        if startend_diff.total_seconds() < 0:
            raise StartAfterEndError()
        return startend_diff

    def assert_pos_duration(duration):
        if duration.total_seconds() < 0:
            raise NegativeDurationError()

    def assert_consistent_triplet(startend_dur, duration):
        diff = startend_dur.total_seconds() - duration.total_seconds()
        if abs(diff) > 1.0:
            raise InconsistentStartEndDurationError()

    if maybe_start and maybe_end and maybe_duration:
        startend_dur = calc_duration(maybe_start, maybe_end)
        assert_pos_duration(maybe_duration)
        assert_consistent_triplet(startend_dur, maybe_duration)
        iv = Interval(maybe_start, startend_dur)
    elif maybe_start and maybe_end:
        startend_dur = calc_duration(maybe_start, maybe_end)
        iv = Interval(maybe_start, startend_dur)
    elif maybe_start and maybe_duration:
        assert_pos_duration(maybe_duration)
        iv = Interval(maybe_start, maybe_duration)
    elif maybe_end and maybe_duration:
        assert_pos_duration(maybe_duration)
        iv = Interval(maybe_end - maybe_duration, maybe_duration)
    else:
        # This case should already be caught at configuration file parse time
        raise RuntimeError('Internal logic error. Please file a bug report')

    return iv


def add_tzinfo(dt: datetime, maybe_tz: Optional[str]) -> datetime:

    # TODO: this could throw an error, right?
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
        dt_aware = specified_tz.localize(dt)
    # Case: specified the timezone and the parsed datetime is timezone-aware
    else:
        # TODO: better error type / message
        raise RuntimeError('TODO')
    return dt_aware


def make_add_tzinfo(maybe_tz: Optional[str]):

    def add_tzinfo(dt: datetime,):

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
            dt_aware = specified_tz.localize(dt)
        # Case: specified the timezone and the parsed datetime is timezone-aware
        else:
            # TODO: better error type / message
            raise RuntimeError('TODO')
        return dt_aware

    if maybe_tz:
        try:
            specified_tz = pytz.timezone(maybe_tz)
        except pytz.exceptions.UnknownTimeZoneError as exc:
            raise TimeZoneParseError(maybe_tz) from exc
    else:
        specified_tz = None

    return add_tzinfo


def create_rawcanon(entry: dict[str, Any]):
    # Note that we can throw an error in `create_interval`
    iv = create_interval(entry['start'], entry['end'], entry['duration'])
    start_str = fmt_time(iv.start)
    duration_str = str(int(iv.duration.total_seconds()))
    worklog = {
        'comment': entry['description'],
        'started': start_str,
        'timeSpentSeconds': duration_str
    }
    return worklog


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
    duration = timedelta(seconds=total_secs)

    return duration


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
