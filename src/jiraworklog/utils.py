#!/usr/bin/env python3

def map_worklogs(f, issues):
    return {k: list(map(f, v)) for k, v in issues.items()}
