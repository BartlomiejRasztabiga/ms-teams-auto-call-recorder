class Meeting:
    def __init__(self, started_at, meeting_id):
        self.started_at = started_at
        self.meeting_id = meeting_id

    def isActive(self):
        return self.meeting_id != -1
