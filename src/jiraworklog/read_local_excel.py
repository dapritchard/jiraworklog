#!/usr/bin/env python3

# from abc import abstractmethod
from datetime import datetime
from functools import total_ordering
from jiraworklog.configuration import Configuration
# from jiraworklog.read_local_delimited import read_local_general, read_worklogs_native
from jiraworklog.read_local_common import (
    LeftError,
    NativeInvalidElement,
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
import openpyxl.worksheet.worksheet
from typing import Callable, Optional, Tuple, Type, Union


class ExcelRow:

    def __init__(
        self,
        row: dict[str, openpyxl.cell.cell.Cell]
    ) -> None:
        self.row = row


@total_ordering
class ExcelInvalidBase(NativeInvalidElement):

    sheet: openpyxl.worksheet.worksheet.Worksheet
    cell: Optional[openpyxl.cell.cell.Cell]

    def __lt__(self, other) -> bool:

        if not isinstance(other, ExcelInvalidBase):
            return False

        # The sheet title takes first priority in ordering
        if self.sheet.title < other.sheet.title:
            return True
        if self.sheet.title > other.sheet.title:
            return False

        # 1. Sheets without an associated cell "tie" sheets with an associated
        # cell
        if not self.cell and not other.cell:
            return False
        # 2. Sheets without an associated cell come before sheets with an
        # associated cell
        if not self.cell and other.cell:
            return True
        # 3. Sheets with an associated cell come after sheets without an
        # associated cell
        if self.cell and not other.cell:
            return False
        # 4. If both sheets have an associated cell then compare the cells
        if self.cell and other.cell:
            if self.cell.row < other.cell.row:
                return True
            if self.cell.row > other.cell.row:
                return False
            # FIXME: this doesn't work right if we have say B and AA
            if self.cell.column_letter < other.cell.column_letter:
                return True
            if self.cell.column_letter > other.cell.column_letter:
                return False
        return False

    # FIXME: it doesn't feel right that we should need this
    def row_index(self) -> int:
        return 1


class ExcelInvalidMissingHeader(ExcelInvalidBase):

    cell: None

    def __init__(
        self,
        sheet: openpyxl.worksheet.worksheet.Worksheet,
        missing_headers: list[str]
    ):
        self.sheet = sheet
        self.cell = None
        self.missing_headers = missing_headers

    def err_msg(self) -> str:
        # TODO: format paragraph?
        msg = (
            f"Worksheet '{self.sheet.title}' header row: the following column "
            "names are specified in the configuration file but are not present "
            f"in the worklogs header line: '{', '.join(self.missing_headers)}'"
        )
        return msg


class ExcelInvalidDuplicateHeader(ExcelInvalidBase):

    cell: None

    def __init__(
        self,
        sheet: openpyxl.worksheet.worksheet.Worksheet,
        duplicate_colnames: list[str]
    ):
        self.sheet = sheet
        self.cell = None
        self.duplicate_colnames = duplicate_colnames

    def err_msg(self) -> str:
        # TODO: format paragraph?
        msg = (
            # TODO: format paragraph?
            f"Worksheet '{self.sheet.title}' header row: the following "
            "duplicate column names were found: "
            f"'{', '.join(self.duplicate_colnames)}'"
        )
        return msg


class ExcelInvalidCellType(ExcelInvalidBase):

    cell: openpyxl.cell.cell.Cell

    def __init__(
        self,
        cell: openpyxl.cell.cell.Cell,
        req_type: Union[Type[int], Type[float], Type[bool], Type[str], Type[datetime], None]
    ):
        self.sheet = cell.parent
        self.cell = cell
        self.req_type = req_type

    # https://support.microsoft.com/en-us/office/data-types-in-data-models-e2388f62-6122-4e2b-bcad-053e3da9ba90
    def err_msg(self):
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
            f"Worksheet '{self.sheet.title}' cell "
            f"{self.cell.column_letter}{self.cell.row}: expected "
            f"{stringify[self.req_type]} but instead observed "
            f"{stringify[type(self.cell.value)]}"
        )
        return msg


# class ExcelMissingHeader(Exception):

#     def __init__(self, missing_colnames):
#         msg = (
#             # TODO: format paragraph?
#             "Error parsing the worklogs file. The following column names are "
#             "specified in the configuration file but are not present in the "
#             f"worklogs header line: '{', '.join(missing_colnames)}'"
#         )
#         super().__init__(msg)


# class ExcelDuplicateHeader(Exception):

#     def __init__(self, missing_colnames):
#         msg = (
#             # TODO: format paragraph?
#             "Error parsing the worklogs file. The following column names are "
#             "specified in the configuration file but are not present in the "
#             f"worklogs header line: '{', '.join(missing_colnames)}'"
#         )
#         super().__init__(msg)


def read_local_excel(
    worklogs_path: str,
    conf: Configuration
) -> dict[str, list[WorklogCanon]]:
    worklogs_native, errors = read_native_worklogs_excel(worklogs_path, conf)
    canon_wkls = create_canon_wkls_excel(worklogs_native, conf, errors)
    return canon_wkls


# https://www.blog.pythonlibrary.org/2021/07/20/reading-spreadsheets-with-openpyxl-and-python/
def read_native_worklogs_excel(
    worklogs_path: str,
    conf: Configuration
) -> Tuple[list[ExcelRow], list[ExcelInvalidBase]]:

    # TODO: need a better error message if this fails?
    workbook = openpyxl.load_workbook(filename=worklogs_path)

    # TODO: we only need the `col_names` out of `create_col_info`
    if conf.parse_excel is None:
        raise RuntimeError('Internal logic error. Please file a bug report')
    col_names, _ = create_col_info(conf.parse_excel)

    entries = []
    errors = []
    for sheet_name in workbook.sheetnames:

        # Grab the sheet and try to read the header row. If there is no header
        # row then give up on the sheet
        sheet = workbook[sheet_name]
        rowiter = sheet.rows
        try:
            header = next(rowiter)
        except:
            continue

        # Map the column letters to the internal column names. If errors are
        # discovered in the header then give up on the sheet
        col_map = {}
        header_values = []
        duplicate_headers = []
        for cell in header:
            if isinstance(cell.value, str) and cell.value in col_names:
                if cell.value in header_values:
                    duplicate_headers.append(cell.value)
                else:
                    header_values.append(cell.value)
                    col_map[cell.column_letter] = cell.value
        missing_headers = set(col_names) - set(col_map.values())
        if missing_headers or duplicate_headers:
            if missing_headers:
                err = ExcelInvalidMissingHeader(sheet, list(missing_headers))
                errors.append(err)
            if duplicate_headers:
                err = ExcelInvalidDuplicateHeader(sheet, duplicate_headers)
                errors.append(err)
            continue

        # Read through the remaining rows. Note that at this point no checking
        # is done on the content of the row elements
        for row in rowiter:
            new_row = {}
            for cell in row:
                # Useful to see what is going on:
                # print(f"{cell.column_letter}{cell.row} = {cell.value} ({type(cell.value)})")
                if cell.column_letter in col_map:
                    new_row[col_map[cell.column_letter]] = cell
            entries.append(ExcelRow(new_row))

    return (entries, errors)


# FIXME: typing
def create_canon_wkls_excel(worklogs_native, conf, errors):
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
        errors=errors
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
