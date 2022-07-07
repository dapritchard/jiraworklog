#!/usr/bin/env python3

import csv
from datetime import datetime
from jiraworklog.configuration import read_conf
import pytz
import re

def read_local_worklogs(worklogs_path):
    conf = read_conf()
    worklogs_native = read_worklogs_native(worklogs_path)
    worklogs = normalize_worklogs_local(worklogs_native, conf)
    return worklogs

def read_worklogs_native(worklogs_path):
    with open(worklogs_path, mode='r') as csv_file:
        entries = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            entries.append(row)
    # TODO: check that columns align with config specifications. E.g. the column
    # labels that are specified exist.
    return entries

def normalize_worklogs_local(entries, conf):
    tags_key = conf['parse_delimited']['col_labels']['tags']
    delimiter2 = conf['parse_delimited']['delimiter2']
    issues_map = conf['issues_map']
    global_tags_set = set(issues_map.keys())
    worklog_parser = create_worklog_parser(conf)
    worklogs = {}
    for entry in entries:
        entry_tags_set = set(entry[tags_key].split(delimiter2))
        tags_intersect = global_tags_set & entry_tags_set
        n_intersect = len(tags_intersect)
        if n_intersect == 0:
            pass
        elif n_intersect == 1:
            id = issues_map[list(tags_intersect)[0]]
            value = worklog_parser(entry)
            if id not in worklogs:
                worklogs[id] = []
            worklogs[id].append(value)
        else:
            # TODO: let's track these and throw an error after the loop
            raise RuntimeError('More than one tag matched')
    return worklogs

def create_worklog_parser(conf):
    col_labels = conf['parse_delimited']['col_labels']
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

def create_worklog_parser_startend(conf):
    col_labels = conf['parse_delimited']['col_labels']
    col_formats = conf['parse_delimited']['col_formats']
    start_key = col_labels['start']
    start_fmt = col_formats['start']
    end_key = col_labels['end']
    end_fmt = col_formats['end']
    description_key = col_labels['description']
    def worklog_parser(entry):
        start = datetime.strptime(entry[start_key], start_fmt)
        end = datetime.strptime(entry[end_key], end_fmt)
        duration_timedelta = end - start
        # TODO: can Jira accept floating point durations? Do we need to truncate
        # to an integer?
        duration_seconds = str(int(duration_timedelta.total_seconds()))
        worklog = {
            'comment': entry[description_key],
            'started': start,
            'timeSpentSeconds': duration_seconds
        }
        return worklog
    return worklog_parser

def make_fmt_time(conf):
    if 'timezone' in conf:
        specified_tz = True
        tz = pytz.timezone(conf['timezone'])
    else:
        specified_tz = False
    def fmt_time(time_str, fmt):
        dt_init = datetime.strptime(time_str, fmt)
        has_tz = not check_tz_naive(dt_init)
        if not specified_tz and not has_tz:
            # TODO: throw error
            pass
        if specified_tz and not has_tz:
            # TODO: have to add time zone
            dt_aware = tz.localize(dt_init)
        else:
            dt_aware = dt_init
        out_init = dt_aware.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        # TODO: change 6-digit %f
        out_mung = out_init
        return out_mung
    return fmt_time

# https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
def check_tz_naive(dt):
    return dt.tzinfo == None or dt.tzinfo.utcoffset(dt) == None

def micro_to_milli(time_str):
    out = re.sub(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3})\d{3}(-\d{4})', "\\1\\2", time_str)
    return out
