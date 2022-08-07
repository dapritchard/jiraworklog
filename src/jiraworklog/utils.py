#!/usr/bin/env python3

from typing import Any

def map_worklogs(f, issues):
    return {k: [f(w) for w in v] for k, v in issues.items()}


def map_worklogs_key(f, worklogs: dict[str, Any]) -> dict[str, Any]:
    out = {k: [f(w, k) for w in v] for k, v in worklogs.items()}
    return out


def map2_issues(f, issues_1, issues_2):
    # TODO: assert that they keys are identical for the two
    out = {k: f(issues_1[k], issues_2[k]) for k in issues_1.keys()}
    return out


def find(val: Any, coll: list[Any]) -> Any:
    for elem in coll:
        if val == elem:
            return elem
    raise RuntimeError('Unable to find the provided value in the collection')
