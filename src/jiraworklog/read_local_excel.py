#!/usr/bin/env python3

from jiraworklog.configuration import Configuration
from jiraworklog.read_local_worklogs import read_worklogs_native
from jiraworklog.worklogs import WorklogCanon
from openpyxl import load_workbook
from typing import Any


# # https://www.blog.pythonlibrary.org/2021/07/20/reading-spreadsheets-with-openpyxl-and-python/
# def read_local_excel(
#     worklogs_path: str,
#     conf: Configuration
# # ) -> dict[str, list[WorklogCanon]]:
# ) -> None:
#     pass


def read_worklogs_native_excel(
    worklogs_path: str,
    conf: Configuration
) -> list[dict[str, Any]]:
    workbook = load_workbook(filename = worklogs_path)
    entries = []
    if conf.parse_excel is None:
        raise RuntimeError('More than one tag matched')
    else:
        colnames = conf.parse_excel['col_labels'].values()
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        rowiter = sheet.rows
        try:
            header = next(rowiter)
        except:
            continue
        col_map = {}
        for cell in header:
            if cell.value in colnames:
                col_map[cell.column_letter] = cell.value
        # TODO: ensure no header elements are None and that they are all strings
        for row in rowiter:
            new_row = {}
            for cell in row:
                # print(f"{cell.column_letter}{cell.row} = {cell.value} ({type(cell.value)})")
                if cell.column_letter in col_map:
                    new_row[col_map[cell.column_letter]] = cell.value
                    # TODO: check type?
            entries.append(new_row)
    return entries

# parse_excel = {
#    'col_labels': {
#         'description': "task",
#         'start': "start",
#         'end': "end",
#         'tags': "tags"
#    }
# }
