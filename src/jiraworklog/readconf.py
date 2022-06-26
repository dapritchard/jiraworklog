#!/usr/bin/env python3

import csv
from datetime import datetime
import yaml

def read_conf():
    with open('../config.yaml', 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    return contents

def read_worklogs_local():
    with open('../worklogs/test-worklog.csv', mode='r') as csv_file:
        entries = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            entries.append(row)
    # TODO: check that columns align with config specifications. E.g. the column
    # labels that are specified exist.
    return entries

def nrml_worklogs_local(worklogs_raw, conf):
    tags_key = conf['tags']
    # comment_key = conf['parse_delimited']['cols_map']['description']
    delimiter2 = conf['parse_delimited']['delimiter2']
    issues = set(conf['tags'].keys())
    worklogs = {}
    for w in worklogs_raw:
        tags_str = w[tags_key]
        tags = set(tags_str.split(delimiter2))
        tags_intersect = tags & issues
        n_intersect = len(tags_intersect)
        if n_intersect == 0:
            pass
        elif n_intersect == 1:
            id = list(tags_intersect)[0]
            # entry = {
            #     comment =
            # }
            if id in worklogs:
                worklogs[id].append()
        # if w['']

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
    def f_start_end(worklog):
        start = datetime.strptime(worklog[start_key], start_fmt)
        end = datetime.strptime(worklog[end_key], end_fmt)
        duration = end - start
        return int(duration.total_seconds())
    return f_start_end

def nrl_worklog_entry(worklog, conf):
    cols_map = conf['parse_delimited']
