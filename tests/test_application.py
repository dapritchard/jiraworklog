#!/usr/bin/env python3

from tests.create_apptest import create_apptest, create_errortest


# Happy-path tests -------------------------------------------------------------

test_01 = create_apptest('tests/data/01-empty-to-empty/')
test_02 = create_apptest('tests/data/02-add-to-empty/')
test_03 = create_apptest('tests/data/03-remove-to-empty/')


# Error-checking tests ---------------------------------------------------------

test_50 = create_errortest(
    'tests/data/50-config-doesnt-exist/',
    FileNotFoundError,
    2,
    'No such file or directory'
)
