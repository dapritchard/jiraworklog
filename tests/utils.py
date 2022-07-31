#!/usr/bin/env python3

from typing import Any

def assert_keys(obj: dict[str, Any], keys: list[str]) -> None:
    assert set(obj.keys()) == set(keys)
