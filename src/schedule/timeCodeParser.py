from dateutil import tz
from datetime import datetime
from .timeCodeParserTypes import (EventType, DateRangeObject, TimeRangeObject, TimeUnit, TimeRange, FreqObject, ByObject,
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
            raise ValueError(f'invalid date: {date}')
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


def parseTimeRange(timeRange: str) -> TimeRangeObject:
    def splitTime(time: str) -> list[str]:
        """
        时间格式：
        hh: mm
        hh
        hh:
        :mm
        :
        """
        timeList: list[str] = time.split(':')
        if len(timeList) > 2 or len(timeList) < 1:
            raise ValueError(f'invalid time: {time}')
        while len(timeList) < 2:
            timeList.append('0')
        return timeList

    res: TimeRangeObject = TimeRangeObject()
    startMark = 0b11
    endMark = 0b11
    if '-' in timeRange:
        start, end = timeRange.split('-')
        [startHour, startMin] = splitTime(start)
        [endHour, endMin] = splitTime(end)
        if '?' in startHour or len(startHour) == 0:
            startMark &= 0b01
            startHour = '0'
        if '?' in startMin or len(startMin) == 0:
            startMark &= 0b10
            startMin = '0'
        if '?' in endHour or len(endHour) == 0:
            endMark &= 0b01
            endHour = '0'
        if '?' in endMin or len(endMin) == 0:
            endMark &= 0b10
            endMin = '0'
        if startMark == 0b01 or endMark == 0b01:
            raise ValueError(f'invalid time range: {timeRange}')
        if (startMark | endMark) >> 1 == 0b1:
            res.start = TimeUnit(int(startHour), int(startMin))
            res.end = TimeUnit(int(endHour), int(endMin))
        else:
            raise ValueError(f'invalid time range: {timeRange}')
    else:
        [endHour, endMin] = splitTime(timeRange)
        if '?' in endHour or '?' in endMin:
            raise ValueError(f'invalid time: {timeRange}')
        res.end = TimeUnit(int(endHour), int(endMin))

    # bin 转为二进制字符串, [2:] 去掉 0b 前缀, zfill(2) 补齐两位
    res.startMark = bin(startMark)[2:].zfill(2)
    res.endMark = bin(endMark)[2:].zfill(2)
    return res

