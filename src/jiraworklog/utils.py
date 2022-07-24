#!/usr/bin/env python3

from typing import Any

def map_worklogs(f, issues):
    return {k: list(map(f, v)) for k, v in issues.items()}


def map_worklogs_key(f, issues):
    out = {k: [f(w, k) for w in v] for k, v in issues.items()}
    return out


def find(val: Any, coll: list[Any]) -> Any:
    for elem in coll:
        if val == elem:
            return elem
    raise RuntimeError('Unable to find the provided value in the collection')
