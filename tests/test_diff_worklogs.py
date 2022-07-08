#!/usr/bin/env python3

localiss = {
    'P9992-3': [
        {'comment': 'Sent from Python today',
         'started': '2021-02-16T12:29:00.000-0500',
         'timeSpentSeconds': 60
         },
        {'comment': 'Another task completed',
         'started': '2021-02-16T14:11:00.000-0500',
         'timeSpentSeconds': 60
         },
        {'comment': 'This is the big one',
         'started': '2021-02-16T15:32:00.000-0500',
         'timeSpentSeconds': 60
         }
    ]
}
localiss_0to2 = {'P9992-3': localiss['P9992-3'][0:2]}
localiss_0to1 = {'P9992-3': localiss['P9992-3'][0:1]}
localiss_0to0 = {'P9992-3': []}
localiss_1to3 = {'P9992-3': localiss['P9992-3'][2:]}
localiss_2to3 = {'P9992-3': localiss['P9992-3'][2:]}

chkiss_3 = {
    'P9992-3': [
        {'author': 'Daffy Duck',
         'comment': 'Sent from Python today',
         'created': '2021-10-03T17:21:55.764-0400',
         'id': '15636',
         'issueId': '16977',
         'started': '2021-02-16T12:29:00.000-0500',
         'timeSpent': '1m',
         'timeSpentSeconds': 60,
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
         'timeSpentSeconds': 60,
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
         'timeSpentSeconds': 60,
         'updateAuthor': 'Daffy Duck',
         'updated': '2021-10-03T17:25:55.122-0400'
         }
    ]
}
chkiss_2 = {'P9992-3': chkiss_3['P9992-3'][0:2]}
chkiss_1 = {'P9992-3': chkiss_3['P9992-3'][0:1]}
chkiss_0 = {'P9992-3': []}
