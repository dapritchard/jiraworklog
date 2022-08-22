#!/usr/bin/env python3

from jiraworklog.configuration import ConfigParseError, create_conferrmsg
from tests.create_apptest import create_apptest, create_errortest


# Application tests ------------------------------------------------------------

test_01 = create_apptest('tests/data/01-empty-to-empty/')
test_02 = create_apptest('tests/data/02-add-to-empty/')
test_03 = create_apptest('tests/data/03-remove-to-empty/')


# Error-checking tests ---------------------------------------------------------

test_50 = create_errortest(
    'tests/data/50-config-doesnt-exist/',
    FileNotFoundError,
    "[Errno 2] No such file or directory: 'tests/data/50-config-doesnt-exist/config.yaml'"
)

test_51 = create_errortest(
    'tests/data/51-config-author-notprovided/',
    ConfigParseError,
    create_conferrmsg([
        "The 'author' field is required but is not provided"
    ])
)
