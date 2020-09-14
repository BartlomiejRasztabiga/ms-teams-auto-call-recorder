class Meeting:
    def __init__(self, started_at=-1, meeting_id=-1):
        self.started_at = started_at
        self.meeting_id = meeting_id

    def isActive(self):
        return self.meeting_id != -1
