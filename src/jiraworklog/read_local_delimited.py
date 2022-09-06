#!/usr/bin/env python3

import csv
from jiraworklog.configuration import Configuration
from jiraworklog.read_local_common import (
    create_canon_wkls,
    make_maybe_parse_time_str,
    make_parse_field,
    make_parse_tags
)
from jiraworklog.worklogs import WorklogCanon
from typing import Any


def read_local_delimited(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native = read_native_wkls_delimited(worklogs_path)
    canon_wkls = create_canon_wkls_delimited(worklogs_native, conf)
    return canon_wkls


# Return a list with each entry a row in the CSV
def read_native_wkls_delimited(worklogs_path: str) -> list[dict[str, Any]]:
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
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_description=make_parse_field(cl['description']),
        parse_start=make_maybe_parse_time_str(cl.get('start'), cf.get('start'), maybe_tz),
        parse_end=make_maybe_parse_time_str(cl.get('end'), cf.get('end'), maybe_tz),
        parse_duration=lambda _: None, # FIXME
        parse_tags=make_parse_tags(cl['tags'], pd.get('delimiter2'))
    )
    return canon_wkls
