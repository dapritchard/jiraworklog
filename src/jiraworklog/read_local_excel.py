#!/usr/bin/env python3

from datetime import datetime
from jiraworklog.configuration import Configuration
# from jiraworklog.read_local_delimited import read_local_general, read_worklogs_native
from jiraworklog.read_local_common import (
    create_canon_wkls,
    make_maybe_parse_duration,
    make_maybe_parse_time_dt,
    make_parse_field,
    make_parse_tags
)
from jiraworklog.worklogs import WorklogCanon
import openpyxl
import openpyxl.cell.cell
from typing import Any, Tuple, Type, Union


class ExcelRow:

    def __init__(self, row):
        self.row = row


class ExcelInvalidCellType:

    def __init__(
        self,
        cell: openpyxl.cell.cell.Cell,
        req_type: Union[Type[int], Type[float], Type[bool], Type[str], Type[datetime], None]
    ):
        self.cell = cell
        self.req_type = req_type

    def err_msg(self):
        # https://support.microsoft.com/en-us/office/data-types-in-data-models-e2388f62-6122-4e2b-bcad-053e3da9ba90
        stringify = {
            int: 'an integer',
            float: 'a decimal number',
            bool: 'a Boolean value',
            str: 'a string',
            datetime: 'a datetime',
            # FIXME: currency?
            None: 'empty'
        }
        stringify[self.req_type]
        msg = (
            f"cell {self.cell.column_letter}{self.cell.row} in sheet "
            f"{self.cell.parent.title} must be {stringify[self.req_type]} but "
            f"is instead {stringify[type(self.cell.value)]}"
        )
        return msg


def read_local_excel(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native, _ = read_native_worklogs_excel(worklogs_path, conf)
    canon_wkls = create_canon_wkls_excel(worklogs_native, conf)
    return canon_wkls


# https://www.blog.pythonlibrary.org/2021/07/20/reading-spreadsheets-with-openpyxl-and-python/
def read_native_worklogs_excel(
    worklogs_path: str,
    conf: Configuration
) -> Tuple[list[dict[str, Any]], list[ExcelInvalidCellType]]:
    # TODO: need a better error message if this fails?
    workbook = openpyxl.load_workbook(filename=worklogs_path)
    entries = []
    # errors = []
    if conf.parse_excel is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    else:
        col_names, col_types = create_col_info(conf.parse_excel)
        print(col_types)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        rowiter = sheet.rows
        try:
            header = next(rowiter)
        except:
            continue
        col_map = {}
        for cell in header:
            if isinstance(cell.value, str) and cell.value in col_names:
                col_map[cell.column_letter] = cell.value
        # TODO: throw error if we don't have all columns
        for row in rowiter:
            new_row = {}
            for cell in row:
                # print(f"{cell.column_letter}{cell.row} = {cell.value} ({type(cell.value)})")
                if cell.column_letter in col_map:
                    # req_type = col_types[col_map[cell.column_letter]]
                    # if isinstance(cell.value, req_type):
                    #     new_row[col_map[cell.column_letter]] = cell.value
                    # else:
                    #     errors.append(ExcelInvalidCellType(cell, req_type))
                    new_row[col_map[cell.column_letter]] = cell.value
            entries.append(ExcelRow(new_row))
    return (entries, [])


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
            entry['description'] = parse_description(entry)
        except Exception as exc:
            entry_errors.append(exc)
        try:
            entry['start'] = parse_start(entry)
        except Exception as exc:
            entry_errors.append(exc)
        try:
            entry['end'] = parse_end(entry)
        except Exception as exc:
            entry_errors.append(exc)
        try:
            entry['duration'] = parse_duration(entry)
        except Exception as exc:
            entry_errors.append(exc)
        try:
            entry['tags'] = parse_tags(entry)
        except Exception as exc:
            entry_errors.append(exc)
        return (parsed_entry, entry_errors)
    return parse_entry


def create_canon_wkls_excel(worklogs_native, conf):
    if conf.parse_excel is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pe = conf.parse_excel
    cl = pe['col_labels']
    maybe_tz = pe.get('timezone')
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_description=make_parse_field(cl['description']),
        parse_start=make_maybe_parse_time_dt(cl.get('start'), maybe_tz),
        parse_end=make_maybe_parse_time_dt(cl.get('end'), maybe_tz),
        parse_duration=make_maybe_parse_duration(cl.get('duration')),
        parse_tags=make_parse_tags(cl['tags'], pe.get('delimiter2'))
    )
    return canon_wkls


def create_col_info(parse_excel):
    col_names = []
    col_types = {}
    type_map = {
        'description': str,
        'start': datetime,
        'end': datetime,
        'duration': str,
        'tags': str
    }
    for k, v in parse_excel['col_labels'].items():
        if v:
            col_names.append(v)
            col_types[v] = type_map[k]
    return (col_names, col_types)
