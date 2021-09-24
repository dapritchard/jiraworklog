#!/usr/bin/env python3

from jira import JIRA
import datetime
import pytz


jira = JIRA(
    server='https://jira.novisci.com',
    basic_auth=('dpritchard', 'XXXXXXXXX')
)

# get issue ID:
# https://confluence.atlassian.com/jirakb/how-to-get-issue-id-from-the-jira-user-interface-827341428.html
issue = jira.issue('21691')

issue_p0053_04 = jira.issue('P0053-4')

print(issue.fields.project.key)            # 'JRA'
print(issue.fields.issuetype.name)         # 'New Feature'
print(issue.fields.reporter.displayName)   # 'Mike Cannon-Brookes [Atlassian]'

worklogs_list = jira.worklogs(issue_p0053_04)
w = worklogs_list[1]
dir(w)
[a for a in dir(w) if not callable(getattr(w, a)) and not a.startswith("_")]
w.author   # we will have to get this information from Jira
w.comment
w.created
w.id
w.issueId
w.raw
w.self
w.started
w.timeSpend
w.timeSpentSeconds
w.updateAuthor
w.updated

[a for a in dir(w) if callable(getattr(w, a)) and not a.startswith("_")]
# w.delete
# w.find
# w.update
#
#
# -----------------------

# method: add_worklog
"""Add a new worklog entry on an issue and return a Resource for it.

:param issue: the issue to add the worklog to
:param timeSpent: a worklog entry with this amount of time spent, e.g. "2d"
:param adjustEstimate: (optional) allows the user to provide specific instructions to update the remaining
  time estimate of the issue. The value can either be ``new``, ``leave``, ``manual`` or ``auto`` (default).
:param newEstimate: the new value for the remaining estimate field. e.g. "2d"
:param reduceBy: the amount to reduce the remaining estimate by e.g. "2d"
:param started: Moment when the work is logged, if not specified will default to now
:param comment: optional worklog comment
:rtype: Worklog
"""

jira.add_worklog(
    issue_p0053_04,
    timeSpent='1m',
    comment='Sent from Python'
)

time_noonish_naive = datetime.datetime(2021, 2, 16, 12, 29)

# create a timezone-aware datetime.
#
# 1. Ideally (is it?) we'd like to grab the user's time-zone settings from Jira
# directly. See
# https://community.atlassian.com/t5/Jira-questions/How-can-I-set-the-JIRA-timezone-accroding-to-the-user-s-location/qaq-p/140142
# for how to look it up in the console.
#
# 2. If we know the offset, then we can probably avoid using `pytz` and just use
# datetime's constructors:
# https://docs.python.org/3/library/datetime.html#timezone-objects (i.e. pytz is
# helpful for named timezones)
#
# 3. There's also the dateutil package (as recommended in the datetime docs):
# https://dateutil.readthedocs.io/en/stable/
tz = pytz.timezone("America/New_York")
time_noonish = tz.localize(time_noonish_naive)

# passing the above version to `add_worklog` doesn't seem to have the effect of
# correctly applying the timezone, so we explicitly convert it to UTC instead
time_converted = time_noonish.astimezone(datetime.timezone.utc)

jira.add_worklog(
    issue_p0053_04,
    timeSpent='1m',
    started=time_converted,
    comment='Sent from Python today at noon'
)
