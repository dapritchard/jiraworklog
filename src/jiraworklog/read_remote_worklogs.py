#!/usr/bin/env python3

from jira import JIRA, JIRAError
from jiraworklog.auth_jira import fmt_jira_error
from jiraworklog.configuration import Configuration
from jiraworklog.worklogs import WorklogJira

class ReadJiraWorkloadError(Exception):

    def __init__(self, wkl_nm: str, jira_error: JIRAError) -> None:
        msg = (
            f"Unable to read the Jira worklog '{wkl_nm}'\n\n"
            f"{fmt_jira_error(jira_error)}"
        )
        super().__init__(msg)


def read_remote_worklogs(
    jira: JIRA,
    conf: Configuration
) -> dict[str, list[WorklogJira]]:
    # TODO: It might be better to collect all of the errors before giving up,
    # but on the other hand that could lead to rather volumninous output so it's
    # not clear what the best thing will be to do
    worklogs = {}
    for wkl_nm in conf.issue_nms:
        try:
            raw_wkls = jira.worklogs(wkl_nm)
        except JIRAError as exc:
            raise ReadJiraWorkloadError(wkl_nm, exc)
        worklogs[wkl_nm] = [WorklogJira(x, wkl_nm) for x in raw_wkls]
    return worklogs
