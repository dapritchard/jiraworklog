#!/usr/bin/env python3

def map_worklogs(f, issues):
    return {k: list(map(f, v)) for k, v in issues.items()}

def map_worklogs_key(f, issues):
    out = {k: [f(w, k) for w in v] for k, v in issues.items()}
    return out
