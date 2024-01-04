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

    def __eq__(self, other):
        if not isinstance(other, DateUnit):
            return False
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __str__(self):
        return f'{self.year}/{self.month}/{self.day}'

    def __repr__(self):
        return f'DateUnit({self.year}, {self.month}, {self.day})'


class DateRangeObject:
    dtstart: DateUnit
    until: DateUnit | None

    def __init__(self, dtstart: DateUnit = DateUnit(), until: DateUnit | None = None):
        self.dtstart = dtstart
        self.until = until

    def __eq__(self, other):
        if not isinstance(other, DateRangeObject):
            return False
        return self.dtstart == other.dtstart and self.until == other.until

    def __str__(self):
        return f'{str(self.dtstart)}-{str(self.until)}'

    def __repr__(self):
        return f'DateRangeObject({self.dtstart}, {self.until})'


class TimeUnit:
    hour: int
    minute: int

    def __init__(self, hour: int = 0, minute: int = 0):
        self.hour = hour
        self.minute = minute

    def __eq__(self, other):
        if not isinstance(other, TimeUnit):
            return False
        return self.hour == other.hour and self.minute == other.minute

    def __str__(self):
        return f'{self.hour}:{self.minute}'

    def __repr__(self):
        return f'TimeUnit({self.hour}, {self.minute})'


class TimeRangeObject:
    start: TimeUnit | None
    end: TimeUnit
    startMark: str
    endMark: str

    def __init__(self, start: TimeUnit | None = None, end: TimeUnit = TimeUnit(), startMark: str = '11', endMark: str = '11'):
        self.start = start
        self.end = end
        self.startMark = startMark
        self.endMark = endMark

    def __eq__(self, other):
        if not isinstance(other, TimeRangeObject):
            return False
        return self.start == other.start and self.end == other.end and self.startMark == other.startMark and self.endMark == other.endMark

    def __str__(self):
        return f'{str(self.start)}-{str(self.end)}'  # TODO time with mark

    def __repr__(self):
        return f'TimeRangeObject({self.start}, {self.end}, {self.startMark}, {self.endMark})'


class TimeRange:
    start: str | None
    end: str
    startMark: str
    endMark: str

    def __init__(self, start: str | None = None, end: str = '', startMark: str = '11', endMark: str = '11'):
        self.start = start
        self.end = end
        self.startMark = startMark
        self.endMark = endMark

    def __eq__(self, other):
        if not isinstance(other, TimeRange):
            return False
        return self.start == other.start and self.end == other.end and self.startMark == other.startMark and self.endMark == other.endMark

    def __str__(self):
        return f'{self.start}-{self.end}'  # TODO time with mark

    def __repr__(self):
        return f'TimeRange({self.start}, {self.end}, {self.startMark}, {self.endMark})'


class FreqObject:
    freq: int
    interval: int | None
    count: int | None

    def __init__(self, freq: int = 0, interval: int | None = None, count: int | None = None):
        self.freq = freq
        self.interval = interval
        self.count = count

    def __eq__(self, other):
        if not isinstance(other, FreqObject):
            return False
        return self.freq == other.freq and self.interval == other.interval and self.count == other.count

    def __str__(self):
        return f'{self.freq}-{self.interval}-{self.count}'

    def __repr__(self):
        return f'FreqObject({self.freq}, {self.interval}, {self.count})'


class ByObject:
    bymonth: list[int] | None
    byweekday: list[weekday] | None
    byweekno: list[int] | None
    byyearday: list[int] | None
    bymonthday: list[int] | None
    byday: list[weekday] | None
    bysetpos: list[int] | None

    def __init__(self, bymonth: list[int] | None = None, byweekday: list[weekday] | None = None, byweekno: list[int] | None = None, byyearday: list[int] | None = None,
                    bymonthday: list[int] | None = None, byday: list[weekday] | None = None, bysetpos: list[int] | None = None):
            self.bymonth = bymonth
            self.byweekday = byweekday
            self.byweekno = byweekno
            self.byyearday = byyearday
            self.bymonthday = bymonthday
            self.byday = byday
            self.bysetpos = bysetpos

    def __eq__(self, other):
        if not isinstance(other, ByObject):
            return False
        return self.bymonth == other.bymonth and self.byweekday == other.byweekday and self.byweekno == other.byweekno and self.byyearday == other.byyearday and \
            self.bymonthday == other.bymonthday and self.byday == other.byday and self.bysetpos == other.bysetpos

    def __str__(self):
        return f'{self.bymonth}-{self.byweekday}-{self.byweekno}-{self.byyearday}-{self.bymonthday}-{self.byday}-{self.bysetpos}'

    def __repr__(self):
        return f'ByObject({self.bymonth}, {self.byweekday}, {self.byweekno}, {self.byyearday}, {self.bymonthday}, {self.byday}, {self.bysetpos})'


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
