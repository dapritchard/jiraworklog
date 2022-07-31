#!/usr/bin/env python3

class JIRAMock:

    def __init__(
        self,
        author: str,
        comment: str,
        created: str,
        id: str,
        issueId: str,
        started: str,
        timeSpent: str,
        timeSpentSeconds: str,
        updateAuthor: str,
        updated: str
    ):
        self.raw = {
            'author': {
                'displayName': author,
            },
            'comment': comment,
            'created': created,
            'id': id,
            'issueId': issueId,
            'started': started,
            'timeSpent': timeSpent,
            'timeSpentSeconds': int(timeSpentSeconds),
            'updateAuthor': {
                'displayName': updateAuthor,
            },
            'updated': updated
        }

    def __repr__(self) -> str:
        return f"<JIRAMock Worklog: id='{self.raw['id']}'>"
