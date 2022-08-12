#!/usr/bin/env python3

import pytest
from tests.create_apptest import create_apptest, exercise_system
from tests.jiramock import JIRAMock
from tests.run_application import run_application

test_01 = create_apptest('tests/data/01-empty-to-empty/')
test_02 = create_apptest('tests/data/02-add-to-empty/')
test_03 = create_apptest('tests/data/03-remove-to-empty/')

# https://docs.pytest.org/en/7.1.x/reference/reference.html#exceptioninfo
# https://docs.python.org/3/library/exceptions.html#OSError
def test_50():
    """Configuration file doesn't exist"""
    with pytest.raises(FileNotFoundError) as exc:
        run_application(
            ['XXXXX.csv',
            '--config-path',
            'tests/data/50-config-doesnt-exist/YYYYY.yaml'
            ],
            JIRAMock(),
            'ZZZZZ.json'
        )
    assert 2 == exc.value.errno
    assert 'No such file or directory' == exc.value.strerror
    assert 'tests/data/50-config-doesnt-exist/YYYYY.yaml' == exc.value.filename
