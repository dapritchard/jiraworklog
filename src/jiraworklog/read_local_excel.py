#!/usr/bin/env python3

from datetime import datetime
from jiraworklog.configuration import Configuration
# from jiraworklog.read_local_delimited import read_local_general, read_worklogs_native
from jiraworklog.read_local_common import (
    LeftError,
    create_canon_wkls,
    # make_maybe_parse_duration,
    # make_maybe_parse_time_dt,
    make_add_tzinfo,
    make_parse_entry,
    make_parse_field,
    # make_parse_tags
    parse_duration
)
from jiraworklog.worklogs import WorklogCanon
import openpyxl
import openpyxl.cell.cell
from typing import Any, Callable, Optional, Tuple, Type, Union


class ExcelRow:

    def __init__(
        self,
        row: dict[str, openpyxl.cell.cell.Cell]
    ) -> None:
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


class ExcelMissingHeader(Exception):

    def __init__(self, missing_colnames):
        msg = (
            "Error parsing the worklogs file. The following column names are "
            "specified in the configuration file but are not present in the "
            f"worklogs header line: '{', '.join(missing_colnames)}'"
        )
        super().__init__(msg)


def read_local_excel(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native = read_native_worklogs_excel(worklogs_path, conf)
    canon_wkls = create_canon_wkls_excel(worklogs_native, conf)
    return canon_wkls


# https://www.blog.pythonlibrary.org/2021/07/20/reading-spreadsheets-with-openpyxl-and-python/
def read_native_worklogs_excel(
    worklogs_path: str,
    conf: Configuration
) -> list[ExcelRow]:
    # TODO: need a better error message if this fails?
    workbook = openpyxl.load_workbook(filename=worklogs_path)
    entries = []
    # errors = []
    if conf.parse_excel is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    else:
        # TODO: we don't need to return the types any more?
        col_names, _ = create_col_info(conf.parse_excel)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        rowiter = sheet.rows
        try:
            header = next(rowiter)
        except:
            continue
        col_map = {}
        # TODO: what about if two cells in the header row have the same column
        # name?
        for cell in header:
            if isinstance(cell.value, str) and cell.value in col_names:
                col_map[cell.column_letter] = cell.value
        missing_headers = set(col_names) - set(col_map.values())
        if missing_headers:
            raise ExcelMissingHeader(missing_headers)
        for row in rowiter:
            new_row = {}
            for cell in row:
                # print(f"{cell.column_letter}{cell.row} = {cell.value} ({type(cell.value)})")
                if cell.column_letter in col_map:
                    new_row[col_map[cell.column_letter]] = cell
            entries.append(ExcelRow(new_row))
    return entries


def create_canon_wkls_excel(worklogs_native, conf):
    if conf.parse_excel is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    pe = conf.parse_excel
    cl = pe['col_labels']
    maybe_tz = pe.get('timezone')
    parse_entry = make_parse_entry(
        parse_description=make_parse_string_excel(cl['description']),
        parse_start=make_parse_dt_excel(cl.get('start'), maybe_tz),
        parse_end=make_parse_dt_excel(cl.get('end'), maybe_tz),
        parse_duration=make_parse_duration_excel(cl.get('duration')),
        parse_tags=make_parse_tags_excel(cl['tags'], pe.get('delimiter2'))
    )
    canon_wkls = create_canon_wkls(
        worklogs_native=worklogs_native,
        issues_map=conf.issues_map,
        parse_entry=parse_entry,
        errors=[]
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


# # TODO: write a comment about `extract_value_excel` not working
# def extract_value_excel(
#     cell: openpyxl.cell.cell.Cell,
#     req_type: Union[Type[str], Type[datetime]]
# ) -> Union[str, datetime]:
#     if type(cell.value) == req_type:
#         return cell.value
#     else:
#         raise LeftError(ExcelInvalidCellType(cell, req_type))


def extract_string_excel(
    cell: openpyxl.cell.cell.Cell
) -> str:
    if type(cell.value) == str:
        return cell.value
    else:
        raise LeftError(ExcelInvalidCellType(cell, str))


def extract_datetime_excel(
    cell: openpyxl.cell.cell.Cell
) -> datetime:
    if type(cell.value) == datetime:
        return cell.value
    else:
        raise LeftError(ExcelInvalidCellType(cell, datetime))


def make_parse_string_excel(
    key: str
# ) -> Callable[[dict[str, openpyxl.cell.cell.Cell]], str]:
) -> Callable[[ExcelRow], str]:
    # def parse_string(entry: dict[str, openpyxl.cell.cell.Cell]):
    def parse_string(entry: ExcelRow):
        cell = extract_cell_excel(entry, key)
        val = extract_string_excel(cell)
        return val
    return parse_string


def make_parse_dt_excel(
    maybe_key: Optional[str],
    maybe_tz: Optional[str]
) -> Callable[[ExcelRow], Optional[datetime]]:
    def parse_dt_excel(entry, key):
        cell = extract_cell_excel(entry, key)
        dt = extract_datetime_excel(cell)
        dt_aware = add_tzinfo(dt)
        return dt_aware
    add_tzinfo = make_add_tzinfo(maybe_tz)
    parse_maybe_dt_excel = make_parse_field(maybe_key, parse_dt_excel)
    return parse_maybe_dt_excel


def make_parse_duration_excel(maybe_key: Optional[str]):
    def parse_duration_excel(entry, key):
        cell = extract_cell_excel(entry, key)
        duration_str = extract_string_excel(cell)
        duration = parse_duration(duration_str)
        return duration
    parse_maybe_duration = make_parse_field(maybe_key, parse_duration_excel)
    return parse_maybe_duration


def make_parse_tags_excel(key, maybe_delimiter2: Optional[str]):
    def parse_tags_excel(entry):
        tags_string = parse_string(entry)
        if maybe_delimiter2:
            tags = set(tags_string.split(maybe_delimiter2))
        else:
            tags = set([tags_string])
        return tags
    parse_string = make_parse_string_excel(key)
    return parse_tags_excel


def extract_cell_excel(row: ExcelRow, key: str) -> openpyxl.cell.cell.Cell:
    return row.row[key]
