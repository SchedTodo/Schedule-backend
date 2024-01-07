from datetime import datetime


class EventBriefVO:
    id: str  # timeId
    scheduleId: str
    name: str
    comment: str
    start: str | None
    end: str
    startMark: str
    endMark: str

    def __init__(self, id: str, scheduleId: str, name: str, comment: str, start: str | None, end: str, startMark: str,
                 endMark: str):
        self.id = id
        self.scheduleId = scheduleId
        self.name = name
        self.comment = comment
        self.start = start
        self.end = end
        self.startMark = startMark
        self.endMark = endMark


class TodoBriefVO:
    id: str  # timeId
    scheduleId: str
    name: str
    end: str
    done: bool

    def __init__(self, id: str, scheduleId: str, name: str, end: str, done: bool):
        self.id = id
        self.scheduleId = scheduleId
        self.name = name
        self.end = end
        self.done = done


class ScheduleBriefVO:
    id: str
    type: str
    name: str
    star: bool
    deleted: bool
    created: datetime
    updated: datetime

    def __init__(self, id: str, type: str, name: str, star: bool, deleted: bool, created: datetime, updated: datetime):
        self.id = id
        self.type = type
        self.name = name
        self.star = star
        self.deleted = deleted
        self.created = created
        self.updated = updated
