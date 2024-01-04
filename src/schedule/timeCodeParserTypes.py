from dateutil.rrule import rrule, weekday


class EventType:
    Event = 'event'
    Todo = 'todo'


class DateUnit:
    year: int
    month: int
    day: int

    def __init__(self, year: int = 0, month: int = 0, day: int = 0):
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f'{self.year}/{self.month}/{self.day}'

    def __repr__(self):
        return f'DateUnit({self.year}, {self.month}, {self.day})'

    def __eq__(self, other):
        if not isinstance(other, DateUnit):
            return False
        return self.year == other.year and self.month == other.month and self.day == other.day


class DateRangeObject:
    dtstart: DateUnit
    until: DateUnit | None

    def __init__(self, dtstart: DateUnit = DateUnit(), until: DateUnit | None = None):
        self.dtstart = dtstart
        self.until = until

    def __str__(self):
        return f'{str(self.dtstart)}-{str(self.until)}'

    def __repr__(self):
        return f'DateRangeObject({self.dtstart}, {self.until})'

    def __eq__(self, other):
        if not isinstance(other, DateRangeObject):
            return False
        return self.dtstart == other.dtstart and self.until == other.until


class TimeUnit:
    hour: int
    minute: int


class TimeRangeObject:
    start: TimeUnit | None
    end: TimeUnit
    startMark: str
    endMark: str


class TimeRange:
    start: str | None
    end: str
    startMark: str
    endMark: str


class FreqObject:
    freq: int
    interval: int | None
    count: int | None


class ByObject:
    bymonth: list[int] | None
    byweekno: list[int] | None
    byyearday: list[int] | None
    bymonthday: list[int] | None
    byday: list[weekday] | None
    bysetpos: list[int] | None


class TimeCodeLex:
    eventType: EventType
    dateRangeObject: DateRangeObject
    timeRangeObject: TimeRangeObject
    timeZone: str
    freqCode: str | None
    byCode: str | None
    newTimeCode: str


class TimeCodeSem:
    times: list[TimeRange]
    rruleObject: rrule


class TimeCodeParseResult:
    eventType: EventType
    times: list[TimeRange]
    rruleObjects: list[rrule]
    newTimeCodes: list[str]


class TimeCodeDao:
    eventType: EventType
    rTimes: list[TimeRange]
    exTimes: list[TimeRange]
    rruleStr: str
    rTimeCodes: str
    exTimeCodes: str
