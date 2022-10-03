#!/usr/bin/env python3

from datetime import datetime
from functools import reduce
from jira import JIRA
# from jiraworklog.delete_worklog import delete_worklog
# from jiraworklog.diff_worklogs import create_augwkl_jira
# from jiraworklog.sync_worklogs import strptime_ptl
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira

# def update_worklogs(jira, checkedin, diff_local, diff_remote):
#     # Note that `checkedin` is modified in the call to `perform_update_actions`
#     update_instrs = create_update_instructions(diff_local, diff_remote)
#     perform_update_actions(jira, checkedin, update_instrs)
#     return checkedin


class UpdateInstructions:

    chk_add_listwkl: list[WorklogJira]
    chk_remove_listwkl: list[WorklogCheckedin]
    rmt_add_listwkl: list[WorklogCanon]
    rmt_remove_listwkl: list[WorklogJira]
    # jira: JIRA

    def __init__(
        self,
        chk_add_listwkl: list[WorklogJira],
        chk_remove_listwkl: list[WorklogCheckedin],
        rmt_add_listwkl: list[WorklogCanon],
        rmt_remove_listwkl: list[WorklogJira],
        # jira: JIRA
    ) -> None:
        self.chk_add_listwkl = chk_add_listwkl
        self.chk_remove_listwkl = chk_remove_listwkl
        self.rmt_add_listwkl = rmt_add_listwkl
        self.rmt_remove_listwkl = rmt_remove_listwkl
        # self.jira = jira

    def push_worklogs(
        self,
        checkedin_wkls: dict[str, list[WorklogCheckedin]],
        jira: JIRA
    ) -> None:
        self.checkedin_add(checkedin_wkls)
        self.checkedin_remove(checkedin_wkls)
        self.remote_add(checkedin_wkls, jira)
        self.remote_remove(checkedin_wkls)

    def checkedin_add(
        self,
        checkedin_wkls: dict[str, list[WorklogCheckedin]]
    ) -> None:
        for wkl in self.chk_add_listwkl:
            update_checkedin_add(checkedin_wkls, wkl)

    def checkedin_remove(
        self,
        checkedin_wkls: dict[str, list[WorklogCheckedin]]
    ) -> None:
        for wkl in self.chk_remove_listwkl:
            update_checkedin_remove(checkedin_wkls, wkl)

    def remote_add(
        self,
        checkedin_wkls: dict[str, list[WorklogCheckedin]],
        jira: JIRA
    ) -> None:
        for wkl in self.rmt_add_listwkl:
            push_worklog_add(checkedin_wkls, wkl, jira)

    def remote_remove(
        self,
        checkedin_wkls: dict[str, list[WorklogCheckedin]]
    ) -> None:
        for wkl in self.rmt_remove_listwkl:
            push_worklog_remove(checkedin_wkls, wkl)


# TODO: is this better than what we had with the flat form?
def update_checkedin_add(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogJira
) -> None:
    checkedin_wkls[jira_wkl.issueKey].append(jira_wkl.to_checkedin())

# TODO: is this better than what we had with the flat form?
def update_checkedin_remove(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogCheckedin
) -> None:
    checkedin_wkls[jira_wkl.issueKey].remove(jira_wkl)

# TODO: is this better than what we had with the flat form?
def push_worklog_add(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    canon_wkl: WorklogCanon,
    jira: JIRA
) -> None:
    # TODO: add error handling?
    raw_jira_wkl = jira.add_worklog(
        issue=canon_wkl.issueKey,
        timeSpentSeconds=canon_wkl.canon['timeSpentSeconds'],
        comment=canon_wkl.canon['comment'],
        started=strptime_ptl(canon_wkl.canon['started'])
    )
    jira_wkl = WorklogJira(raw_jira_wkl, canon_wkl.issueKey)
    update_checkedin_add(checkedin_wkls, jira_wkl)

# TODO: is this better than what we had with the flat form?
def push_worklog_remove(
    checkedin_wkls: dict[str, list[WorklogCheckedin]],
    jira_wkl: WorklogJira
) -> None:
    jira_wkl.jira.delete()
    update_checkedin_remove(checkedin_wkls, jira_wkl)


def strptime_ptl(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')


# TODO: move this? Maybe `calc_n_updates` too?
def calc_issue_max_strwidth(update_instr):
    def update_maxlen(maxlen, listwkl):
        for x in listwkl:
            if len(x.issueKey) > maxlen:
                maxlen = len(x.issueKey)
        return maxlen
    maxlen = reduce(
        update_maxlen,
        [update_instr.chk_add_listwkl,
         update_instr.chk_remove_listwkl,
         update_instr.rmt_add_listwkl,
         update_instr.rmt_remove_listwkl
         ],
        0
    )
    return maxlen


def calc_n_updates(update_instrs: UpdateInstructions):
    n_updates = (
        len(update_instrs.chk_add_listwkl)
        + len(update_instrs.chk_remove_listwkl)
        + len(update_instrs.rmt_add_listwkl)
        + len(update_instrs.rmt_remove_listwkl)
    )
    return n_updates



# # TODO: is this better than what we had with the flat form?
# def push_worklogs_NEW(
#     jira: JIRA,
#     checkedin_wkls: dict[str, list[WorklogCheckedin]],
#     update_instrs: UpdateInstrs
# ):
#     chk_1 = reduce(update_checkedin_add, update_instrs.checkedin_add, checkedin_wkls)
#     chk_2 = reduce(update_checkedin_remove, update_instrs.checkedin_remove, chk_1)
#     chk_3 = reduce(lambda x,y: push_worklog_add(x, y, jira), update_instrs.remote_add, chk_2)
#     chk_4 = reduce(push_worklog_remove, update_instrs.remote_remove, chk_3)
#     return chk_4

# def push_worklogs(jira, checkedin, update_instrs):
#     for instr in update_instrs:
#         if instr.pop('remote'):
#             maybe_jira_wkl = update_remote(jira, **instr)
#             if maybe_jira_wkl is not None:
#                 instr['augwkl'] = create_augwkl_jira(maybe_jira_wkl)
#         update_checkedin(checkedin, **instr)

# def update_checkedin(checkedin, action, issue, augwkl):
#     assert action in ['added', 'removed']
#     if action == 'added':
#         # TODO: consider sorting by start time?
#         checkedin[issue].append(augwkl)
#     else:
#         found_match = False
#         for i, augwkl_checkedin in enumerate(checkedin[issue]):
#             if augwkl_checkedin['canon'] == augwkl['canon']:
#                 found_match = True
#                 del checkedin[issue][i]
#                 continue
#         if not found_match:
#             raise RuntimeError('Internal logic error. Please file a bug report')

# def update_remote(jira, action, issue, augwkl):
#     assert action in ['added', 'removed']
#     if action == 'added':
#         canon = augwkl['canon']
#         maybe_jira_wkl = jira.add_worklog(
#             issue=issue,
#             timeSpentSeconds=canon['timeSpentSeconds'],
#             comment=canon['comment']
#         )
#     else:
#         full = augwkl['full']
#         jira_wkl = jira.worklog(full['issueId'], full['id'])
#         maybe_jira_wkl = jira_wkl.delete()
#     return maybe_jira_wkl

# # def add_checkedin(iss_checkedin, iss_key, augwkl_local):
# #     found_match = False
# #     for i, augwkl_checkedin in enumerate(iss_checkedin[iss_key]):
# #         if augwkl_checkedin['canon'] == augwkl_local['canon']:
# #             found_match = True
# #             iss_checkedin.pop(i)
# #             continue
# #     if not found_match:
# #         raise RuntimeError('Internal logic error. Please file a bug report')
