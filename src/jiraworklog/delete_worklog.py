#!/usr/bin/env python3

from jira.client import translate_resource_args
from jira.resources import Issue, Worklog
from requests import Response
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    no_type_check,
    overload,
)


@translate_resource_args
def delete_worklog(
    # self,
    jira,
    issue: (Union[Issue, str]),
    worklog: (Union[Worklog, str]),
    adjustEstimate: (Optional[str]) = None,
    newEstimate: (Optional[str]) = None,
    increaseBy: (Optional[str]) = None,
) -> Response:
    """Delete a worklog entry

    Args:
        issue: (Union[Issue, str]): the issue from which the worklog is to be removed
        worklog: (Union[Worklog, str]): the worklog to remove
        adjustEstimate (Optional[str]):  allows the user to provide specific instructions to update
            the remaining time estimate of the issue. The value can either be ``new``, ``leave``, ``manual`` or ``auto`` (default).
        newEstimate (Optional[str]): the new value for the remaining estimate field. e.g. "2d"
        increaseBy (Optional[str]): the amount to increase the remaining estimate by e.g. "2d"
    Returns:
        Worklog
    """
    if isinstance(issue, Issue):
        issue = issue.id

    params = {}
    if adjustEstimate is not None:
        params["adjustEstimate"] = adjustEstimate
    if newEstimate is not None:
        params["newEstimate"] = newEstimate
    if increaseBy is not None:
        params["increaseBy"] = increaseBy

    # url = self._get_url(f"issue/{issue}/worklog/{worklog}")
    # return self._session.delete(url, params=params)
    url = jira._get_url(f"issue/{issue}/worklog/{worklog}")
    return jira._session.delete(url, params=params)
