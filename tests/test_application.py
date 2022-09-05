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

# test_51 = create_errortest(
#     'tests/data/51-config-author-notprovided/',
#     ConfigParseError,
#     create_conferrmsg([
#         "The 'author' field is required but is not provided"
#     ])
# )

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/03-remove-to-empty/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc
# # e.validator.error_handler(e.validator._errors)

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/51-config-no-author/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/52-config-author-wrongtype/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/53-config-authentication-notprovided/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/54-config-authentication-notmapping/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/55-config-issuesmap-notprovided/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/56-config-issuesmap-notmapping/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/65-config-timezone-wrongtype/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/75-checkedinpath-wrongtype/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/78-config-parsetype-notprovided/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/79-config-parsetype-wrongtype/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc

# import jiraworklog.configuration
# try:
#     import tests.create_apptest
#     tests.create_apptest.exercise_system('tests/data/81-config-parsedelimited-wrongtype/', ['--auto-confirm'])
# except jiraworklog.configuration.ConfigParseError as exc:
#     e = exc
