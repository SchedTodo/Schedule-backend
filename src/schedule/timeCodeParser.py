from dateutil import tz
from datetime import datetime
from .timeCodeParserTypes import (EventType, DateRangeObject, TimeRangeObject, TimeRange, FreqObject, ByObject,
                                  TimeCodeLex, TimeCodeSem, TimeCodeParseResult, TimeCodeDao, DateUnit)
from .userSettings import getSettingsByPath


def parseDateRange(dateRange: str) -> DateRangeObject:
    def parseDate(date: str) -> {int | None, int | None, int | None}:
        """
        日期格式：
        yyyy/m/d
        m/d
        d
        """
        dateList: list[str | None] = date.split('/')
        if len(dateList) > 3 or len(dateList) < 1:
            raise ValueError(f'invalide date: {date}')
        while len(dateList) < 3:
            dateList.insert(0, None)
        year, month, day = map(lambda x: int(x) if x is not None else None, dateList)
        return {'year': year, 'month': month, 'day': day}

    res: DateRangeObject = DateRangeObject(DateUnit())
    if '-' in dateRange:
        [dtstart, until] = map(parseDate, dateRange.split('-'))
        for key, value in until.items():
            if value is None:
                until[key] = dtstart[key]
        res.dtstart = DateUnit(**dtstart)
        res.until = DateUnit(**until)
    else:
        dtstart = parseDate(dateRange)
        res.dtstart = DateUnit(**dtstart)
    if res.dtstart.year is None:
        now = datetime.now().astimezone(tz.gettz(getSettingsByPath('rrule.timeZone')))
        # 如果 dtstart 没有年份，且 dtstart < now，则 dtstart 的年份为下一年
        if (res.dtstart.month is not None and res.dtstart.month < now.month
                and res.dtstart.day is not None and res.dtstart.day < now.day):
            res.dtstart.year = now.year + 1
        else:
            res.dtstart.year = now.year
        if res.until is not None and res.until.year is None:
            res.until.year = res.dtstart.year
    return res
