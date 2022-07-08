#!/usr/bin/env python3

from jira.client import translate_resource_args
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
    issue,
    id: (Optional[str]) = None,
    adjustEstimate: (Optional[str]) = None,
    newEstimate: (Optional[str]) = None,
    increaseBy: (Optional[str]) = None,
) -> Response:
    """Add a new worklog entry on an issue and return a Resource for it.

    Args:
        issue (str): the issue to add the worklog to
        timeSpent (Optional[str]): a worklog entry with this amount of time spent, e.g. "2d"
        timeSpentSeconds (Optional[str]): a worklog entry with this amount of time spent in seconds
        adjustEstimate (Optional[str]):  allows the user to provide specific instructions to update
            the remaining time estimate of the issue. The value can either be ``new``, ``leave``, ``manual`` or ``auto`` (default).
        newEstimate (Optional[str]): the new value for the remaining estimate field. e.g. "2d"
        increaseBy (Optional[str]): the amount to reduce the remaining estimate by e.g. "2d"
        comment (Optional[str]): optional worklog comment
        started (Optional[datetime.datetime]): Moment when the work is logged, if not specified will default to now
        user (Optional[str]): the user ID or name to use for this worklog
    Returns:
        Worklog
    """
    params = {}
    if adjustEstimate is not None:
        params["adjustEstimate"] = adjustEstimate
    if newEstimate is not None:
        params["newEstimate"] = newEstimate
    if increaseBy is not None:
        params["increaseBy"] = increaseBy

    # url = self._get_url(f"issue/{issue}/worklog/{id}")
    # return self._session.delete(url, params=params)
    url = jira._get_url(f"issue/{issue}/worklog/{id}")
    return jira._session.delete(url, params=params)
