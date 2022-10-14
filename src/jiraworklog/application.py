#!/usr/bin/env python3

from jiraworklog.auth_jira import auth_jira
from jiraworklog.cmdline_args import parser
from jiraworklog.configuration import read_conf
from jiraworklog.init_config import init_config
from jiraworklog.sync_worklogs import sync_worklogs
import sys
from typing import Optional


# Created with the intention of being used in an expression such as
# `sys.exit(main())` as is the case with Setuptools entry points shim scripts.
#
# The return object is therefore designed to conform to sys.exit's API. From
# https://docs.python.org/3/library/sys.html#sys.exit:
#
#     None is equivalent to passing zero, and any other object is printed to
#     stderr and results in an exit code of 1.
#
def main() -> Optional[str]:

    cmdline_args = parser.parse_args()
    # TODO: let's extract this into a routine somewhere that encapsulates the
    # above call
    if not (0 <= cmdline_args.verbose and cmdline_args.verbose <= 2):
        msg = (
            "Error: the --verbose argument must be an integer between 0 and 2, "
            f"but the input value was '{cmdline_args.verbose}'"
        )
        return msg

    if cmdline_args.init_config:
        init_config()
        return None

    is_need_response = not (cmdline_args.auto_confirm or cmdline_args.dry_run)
    if not cmdline_args.file and is_need_response:
        msg = 'Error: must have set --auto-confirm when reading worklogs from standard input'
        sys.exit(msg)

    try:
        conf = read_conf(cmdline_args.config_path)
        jira = auth_jira(conf)
        sync_worklogs(jira, conf, cmdline_args, cmdline_args.file, True)
    except Exception as exc:
        if cmdline_args.verbose >= 2:
            raise RuntimeError('Error running jiraworklog') from exc
        return(str(exc))
    return None
