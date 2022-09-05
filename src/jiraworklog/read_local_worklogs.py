#!/usr/bin/env python3

import csv
from datetime import datetime
from jiraworklog.configuration import Configuration, ParseType
from jiraworklog.read_checkedin_worklogs import align_checkedin_with_conf
from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogCanon
import pytz
import re
from typing import Any, Callable


def read_local_delimited(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native = read_worklogs_native(worklogs_path)
    worklogs = read_local_general(worklogs_native, conf)
    return worklogs


def read_local_general(
    worklogs_native, #  TODO: type
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_parsed = normalize_worklogs_local(worklogs_native, conf)
    align_checkedin_with_conf(worklogs_parsed, conf)
    worklogs = map_worklogs_key(WorklogCanon, worklogs_parsed)
    return worklogs


# Return a list with each entry a row in the CSV
# TODO: change this and other functions' names to something like `read_local_native`?
def read_worklogs_native(worklogs_path: str) -> list[dict[str, Any]]:
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


def normalize_worklogs_local(
    entries: list[dict[str, Any]],
    conf: Configuration
) -> dict[str, Any]:
    tags_key = conf.parse_delimited['col_labels']['tags']
    delimiter2 = conf.parse_delimited['delimiter2']
    # TODO: make this a field in Configuration?
    global_tags_set = set(conf.issues_map.keys())
    worklog_parser = create_worklog_parser(conf)
    worklogs = {}
    for entry in entries:
        entry_tags_set = set(entry[tags_key].split(delimiter2))
        tags_intersect = global_tags_set & entry_tags_set
        n_intersect = len(tags_intersect)
        if n_intersect == 0:
            pass
        elif n_intersect == 1:
            id = conf.issues_map[list(tags_intersect)[0]]
            value = worklog_parser(entry)
            if id not in worklogs:
                worklogs[id] = []
            worklogs[id].append(value)
        else:
            # TODO: let's track these and throw an error after the loop
            raise RuntimeError('More than one tag matched')
    return worklogs


def create_worklog_parser(
    conf: Configuration
) -> Callable[[dict[str, Any]], dict[str, str]]:
    col_labels = conf.parse_delimited['col_labels']
    has_start = col_labels.get("start") is not None
    has_end = col_labels.get("end") is not None
    has_duration = col_labels.get("duration") is not None
    if has_start and has_end:
        retval = create_worklog_parser_startend(conf)
    elif has_start and has_duration:
        raise RuntimeError('Not yet implemented: has_start and has_duration')
    elif has_end and has_duration:
        raise RuntimeError('Not yet implemented: has_end and has_duration')
    else:
        # TODO: should this case be checked at config parse time?
        raise RuntimeError('Need at least two out of three: start time, end time, or duration')
    return retval


def create_worklog_parser_startend(
    conf: Configuration
) -> Callable[[dict[str, Any]], dict[str, str]]:
    def create_parse_fromstr(entry_key, datetime_fmt):
        def parse_fromtstr(entry):
            return datetime.strptime(entry[entry_key], datetime_fmt)
        return parse_fromtstr
    if conf.parse_delimited is not None:
        cl = conf.parse_delimited['col_labels']
        cf = conf.parse_delimited['col_formats']
        parse_start = create_parse_fromstr(cl['start'], cf['start'])
        parse_end = create_parse_fromstr(cl['end'], cf['end'])
    elif conf.parse_excel is not None:
        cl = conf.parse_excel['col_labels']
        parse_start = lambda entry: entry[cl['start']]
        parse_end = lambda entry: entry[cl['end']]
    else:
        raise RuntimeError('Internal logic error. Please file a bug report')
    description_key = cl['description']
    # col_labels = conf.parse_delimited['col_labels']
    # col_formats = conf.parse_delimited['col_formats']
    # start_key = col_labels['start']
    # end_key = col_labels['end']
    # start_fmt = col_formats['start']
    # end_fmt = col_formats['end']
    # description_key = col_labels['description']
    fmt_time = make_fmt_time(conf)
    def worklog_parser(entry: dict[str, Any]) -> dict[str, str]:
        start = parse_start(entry)
        end = parse_end(entry)
        duration_timedelta = end - start
        duration_str = str(int(duration_timedelta.total_seconds()))
        start_str = fmt_time(start)
        worklog = {
            'comment': entry[description_key],
            'started': start_str,
            'timeSpentSeconds': duration_str
        }
        return worklog
    return worklog_parser


def make_fmt_time(conf: Configuration) -> Callable[[datetime], str]:

    if conf.parse_delimited is not None:
        tz_maybestr = conf.parse_delimited.get('timezone')
    elif conf.parse_excel is not None:
        tz_maybestr = conf.parse_excel.get('timezone')
    else:
        raise RuntimeError('Internal logic error. Please file a bug report')

    if tz_maybestr is None:
        specified_tz = None
    else:
        specified_tz = pytz.timezone(tz_maybestr)

    def fmt_time(dt: datetime) -> str:
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
        out_init = dt_aware.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        out_mung = micro_to_milli(out_init)
        return out_mung

    return fmt_time


# https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
def check_tz_naive(dt: datetime) -> bool:
    return dt.tzinfo == None or dt.tzinfo.utcoffset(dt) == None


def micro_to_milli(time_str: str) -> str:
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3})\d{3}(-\d{4})'
    out = re.sub(pattern, "\\1\\2", time_str)
    return out
