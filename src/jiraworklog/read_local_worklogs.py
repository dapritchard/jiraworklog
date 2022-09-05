#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
from jiraworklog.configuration import Configuration, ParseType
from jiraworklog.read_checkedin_worklogs import align_checkedin_with_conf
from jiraworklog.utils import map_worklogs_key
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


def read_local_delimited(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native = read_worklogs_native_delimited(worklogs_path)
    canon_wkls = create_canon_wkls_delimited(worklogs_native, conf)
    return canon_wkls


# Return a list with each entry a row in the CSV
# TODO: change this and other functions' names to something like `read_local_native`?
def read_worklogs_native_delimited(worklogs_path: str) -> list[dict[str, Any]]:
    # TODO: is error handling needed? E.g. wrong number of columns
    with open(worklogs_path, mode='r') as csv_file:
        entries = []
        # TODO: support other delimiters and options
        reader = csv.DictReader(csv_file)
        for row in reader:
            entries.append(row)
    # TODO: check that columns align with config specifications. E.g. the column
    # labels that are specified exist.
    return entries


def create_canon_wkls_delimited(worklogs_native, conf):
    if conf.parse_delimited is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pd = conf.parse_delimited
    cl = pd['col_labels']
    cf = pd['col_formats']
    maybe_tz = pd.get('timezone')
    parse_worklogs = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_description=make_parse_field(cl['description']),
        parse_start=make_maybe_parse_time_str(cl.get('start'), cf.get('start'), maybe_tz),
        parse_end=make_maybe_parse_time_str(cl.get('end'), cf.get('end'), maybe_tz),
        parse_duration=lambda _: None, # FIXME
        parse_tags=make_parse_tags(cl['tags'], pd.get('delimiter2'))
    )
    return parse_worklogs


# def read_local_general(
#     worklogs_native, #  TODO: type
#     conf: Configuration
# ) -> dict[str, list[WorklogCanon]]:
#     worklogs_parsed = normalize_worklogs_local(worklogs_native, conf)
#     align_checkedin_with_conf(worklogs_parsed, conf)
#     worklogs = map_worklogs_key(WorklogCanon, worklogs_parsed)
#     return worklogs


# def construct_canon_wkls(
#     worklogs_native, #  TODO: type (and below)
#     create_raw_canon_wkls,
#     conf: Configuration
# ) -> dict[str, list[WorklogCanon]]:
#     raw_local_worklogs = create_raw_canon_wkls(worklogs_native)
#     align_checkedin_with_conf(raw_local_worklogs, conf)
#     worklogs = map_worklogs_key(WorklogCanon, raw_local_worklogs)
#     return worklogs


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


# def normalize_worklogs_local(
#     entries: list[dict[str, Any]],
#     conf: Configuration
# ) -> dict[str, Any]:
#     tags_key = conf.parse_delimited['col_labels']['tags']
#     delimiter2 = conf.parse_delimited['delimiter2']
#     # TODO: make this a field in Configuration?
#     global_tags_set = set(conf.issues_map.keys())
#     worklog_parser = create_worklog_parser(conf)
#     worklogs = {}
#     for entry in entries:
#         entry_tags_set = set(entry[tags_key].split(delimiter2))
#         tags_intersect = global_tags_set & entry_tags_set
#         n_intersect = len(tags_intersect)
#         if n_intersect == 0:
#             pass
#         elif n_intersect == 1:
#             id = conf.issues_map[list(tags_intersect)[0]]
#             value = worklog_parser(entry)
#             if id not in worklogs:
#                 worklogs[id] = []
#             worklogs[id].append(value)
#         else:
#             # TODO: let's track these and throw an error after the loop
#             raise RuntimeError('More than one tag matched')
#     return worklogs


# def create_worklog_parser(
#     conf: Configuration
# ) -> Callable[[dict[str, Any]], dict[str, str]]:
#     col_labels = conf.parse_delimited['col_labels']
#     has_start = col_labels.get("start") is not None
#     has_end = col_labels.get("end") is not None
#     has_duration = col_labels.get("duration") is not None
#     if has_start and has_end:
#         retval = create_worklog_parser_startend(conf)
#     elif has_start and has_duration:
#         raise RuntimeError('Not yet implemented: has_start and has_duration')
#     elif has_end and has_duration:
#         raise RuntimeError('Not yet implemented: has_end and has_duration')
#     else:
#         # TODO: should this case be checked at config parse time?
#         raise RuntimeError('Need at least two out of three: start time, end time, or duration')
#     return retval


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


def make_parse_tags(tags_key: str, maybe_delimiter2: Optional[str]): # TODO: return type
    if maybe_delimiter2 is None:
        return lambda entry: set(entry[tags_key])
    else:
        return lambda entry: set(entry[tags_key].split(maybe_delimiter2))


# def create_worklog_parser_startend(
#     conf: Configuration
# ) -> Callable[[dict[str, Any]], dict[str, str]]:
#     def create_parse_fromstr(entry_key, datetime_fmt):
#         def parse_fromtstr(entry):
#             return datetime.strptime(entry[entry_key], datetime_fmt)
#         return parse_fromtstr
#     if conf.parse_delimited is not None:
#         cl = conf.parse_delimited['col_labels']
#         cf = conf.parse_delimited['col_formats']
#         parse_start = create_parse_fromstr(cl['start'], cf['start'])
#         parse_end = create_parse_fromstr(cl['end'], cf['end'])
#     elif conf.parse_excel is not None:
#         cl = conf.parse_excel['col_labels']
#         parse_start = lambda entry: entry[cl['start']]
#         parse_end = lambda entry: entry[cl['end']]
#     else:
#         raise RuntimeError('Internal logic error. Please file a bug report')
#     description_key = cl['description']
#     # col_labels = conf.parse_delimited['col_labels']
#     # col_formats = conf.parse_delimited['col_formats']
#     # start_key = col_labels['start']
#     # end_key = col_labels['end']
#     # start_fmt = col_formats['start']
#     # end_fmt = col_formats['end']
#     # description_key = col_labels['description']
#     fmt_time = make_fmt_time(conf)
#     def worklog_parser(entry: dict[str, Any]) -> dict[str, str]:
#         start = parse_start(entry)
#         end = parse_end(entry)
#         duration_timedelta = end - start
#         duration_str = str(int(duration_timedelta.total_seconds()))
#         start_str = fmt_time(start)
#         worklog = {
#             'comment': entry[description_key],
#             'started': start_str,
#             'timeSpentSeconds': duration_str
#         }
#         return worklog
#     return worklog_parser


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


# def make_fmt_time(conf: Configuration) -> Callable[[datetime], str]:

#     if conf.parse_delimited is not None:
#         tz_maybestr = conf.parse_delimited.get('timezone')
#     elif conf.parse_excel is not None:
#         tz_maybestr = conf.parse_excel.get('timezone')
#     else:
#         raise RuntimeError('Internal logic error. Please file a bug report')

#     if tz_maybestr is None:
#         specified_tz = None
#     else:
#         specified_tz = pytz.timezone(tz_maybestr)

#     def fmt_time(dt: datetime) -> str:
#         has_tz = not check_tz_naive(dt)
#         # Case: didn't specify the timezone and the parsed datetime isn't
#         # timezone-aware
#         if specified_tz is None and not has_tz:
#             # TODO: better error type / message
#             raise RuntimeError('TODO')
#         # Case: didn't specify the timezone and the parsed datetime is
#         # timezone-aware
#         if specified_tz is None and has_tz:
#             dt_aware = dt
#         # Case: specified the timezone and the parsed datetime isn't
#         # timezone-aware
#         if specified_tz is not None and not has_tz:
#             # TODO: have to add time zone
#             dt_aware = specified_tz.localize(dt)
#         # Case: specified the timezone and the parsed datetime is timezone-aware
#         else:
#             # TODO: better error type / message
#             raise RuntimeError('TODO')
#         out_init = dt_aware.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
#         out_mung = micro_to_milli(out_init)
#         return out_mung

#     return fmt_time


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
