#!/usr/bin/env python3

from jiraworklog.utils import map_worklogs_key
from jiraworklog.worklogs import WorklogCanon, WorklogCheckedin, WorklogJira
from tests.jiramock import JIRAMock


raw_local_wkls = {
    'P9992-3': [
        {'comment': 'Sent from Python today',
         'started': '2021-02-16T12:29:00.000-0500',
         'timeSpentSeconds': '60'
         },
        {'comment': 'Another task completed',
         'started': '2021-02-16T14:11:00.000-0500',
         'timeSpentSeconds': '60'
         },
        {'comment': 'This is the big one',
         'started': '2021-02-16T15:32:00.000-0500',
         'timeSpentSeconds': '60'
         }
    ]
}
local_wkls = map_worklogs_key(WorklogCanon, raw_local_wkls)
local_0to2 = {'P9992-3': local_wkls['P9992-3'][0:2]}
local_0to1 = {'P9992-3': local_wkls['P9992-3'][0:1]}
local_0to0 = {'P9992-3': []}
local_1to3 = {'P9992-3': local_wkls['P9992-3'][1:]}
local_2to3 = {'P9992-3': local_wkls['P9992-3'][2:]}
localtwo_wkls = {
    'P7777-7': [WorklogCanon(w.canon, 'P7777-7') for w in local_wkls['P9992-3']],
    'P9992-3': local_wkls['P9992-3']
}


raw_checkedin_wkls = {
    'P9992-3': [
        {'author': 'Daffy Duck',
         'comment': 'Sent from Python today',
         'created': '2021-10-03T17:21:55.764-0400',
         'id': '15636',
         'issueId': '16977',
         'started': '2021-02-16T12:29:00.000-0500',
         'timeSpent': '1m',
         'timeSpentSeconds': '60',
         'updateAuthor': 'Daffy Duck',
         'updated': '2021-10-03T17:21:55.764-0400'
         },
        {'author': 'Daffy Duck',
         'comment': 'Another task completed',
         'created': '2021-10-03T17:22:06.923-0400',
         'id': '76655',
         'issueId': '16977',
         'started': '2021-02-16T14:11:00.000-0500',
         'timeSpent': '1m',
         'timeSpentSeconds': '60',
         'updateAuthor': 'Daffy Duck',
         'updated': '2021-10-03T17:22:06.923-0400'
         },
        {'author': 'Daffy Duck',
         'comment': 'This is the big one',
         'created': '2021-10-03T17:25:55.122-0400',
         'id': '90210',
         'issueId': '16977',
         'started': '2021-02-16T15:32:00.000-0500',
         'timeSpent': '1m',
         'timeSpentSeconds': '60',
         'updateAuthor': 'Daffy Duck',
         'updated': '2021-10-03T17:25:55.122-0400'
         }
    ]
}
checkedin_wkls = map_worklogs_key(WorklogCheckedin, raw_checkedin_wkls)
checkedin_0to2 = {'P9992-3': checkedin_wkls['P9992-3'][0:2]}
checkedin_0to1 = {'P9992-3': checkedin_wkls['P9992-3'][0:1]}
checkedin_0to0 = {'P9992-3': []}
checkedin_1to3 = {'P9992-3': checkedin_wkls['P9992-3'][1:]}
checkedin_2to3 = {'P9992-3': checkedin_wkls['P9992-3'][2:]}
checkedintwo_wkls = {
    'P7777-7': [WorklogCheckedin(w.full, 'P7777-7') for w in checkedin_wkls['P9992-3']],
    'P9992-3': checkedin_wkls['P9992-3']
}

raw_remote_wkls = {
    k: [JIRAMock(**w) for w in v]
    for k, v in
    raw_checkedin_wkls.items()
}
remote_wkls = map_worklogs_key(WorklogJira, raw_remote_wkls)
remote_0to2 = {'P9992-3': remote_wkls['P9992-3'][0:2]}
remote_0to1 = {'P9992-3': remote_wkls['P9992-3'][0:1]}
remote_0to0 = {'P9992-3': []}
remote_1to3 = {'P9992-3': remote_wkls['P9992-3'][1:]}
remote_2to3 = {'P9992-3': remote_wkls['P9992-3'][2:]}
remotetwo_wkls = {
    'P7777-7': [WorklogJira(w.jira, 'P7777-7') for w in remote_wkls['P9992-3']],
    'P9992-3': remote_wkls['P9992-3']
}
