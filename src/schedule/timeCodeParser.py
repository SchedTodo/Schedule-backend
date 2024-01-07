import re

import dateutil
from dateutil import tz
from dateutil.relativedelta import relativedelta
from datetime import datetime

from dateutil.rrule import DAILY, WEEKLY, MONTHLY, YEARLY, weekdays, weekday, MO, TU, WE, TH, FR, SA, SU, rrule

from src.schedule.timeCodeParserTypes import (EventType, DateRangeObject, TimeRangeObject, TimeUnit, TimeRange,
                                              FreqObject, ByObject, TimeCodeLex, TimeCodeSem, TimeCodeParseResult, TimeCodeDao, DateUnit)
from src.schedule.userSettings import getSettingsByPath
from src.utils.timeZone import isValidTimeZone, getTimeZoneAbbrMap
from src.utils.utils import intersection, difference

timeZoneAbbrMap = getTimeZoneAbbrMap()


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

    # bin 转为二进制字符串，[2:] 去掉 0b 前缀，zfill(2) 补齐两位
    res.startMark = bin(startMark)[2:].zfill(2)
    res.endMark = bin(endMark)[2:].zfill(2)
    return res


def parseFreq(freqCode: str) -> FreqObject:
    res = FreqObject()
    freq: str
    if ',' in freqCode:
        _freq, *args = freqCode.split(',')
        freq = _freq
        for arg in args:
            if arg[0] == 'i':
                # 是 interval
                try:
                    interval = int(arg[1:])
                except ValueError:
                    raise ValueError(f'invalid interval: {arg}')
                if interval < 0:
                    raise ValueError(f'invalid interval: {arg}')
                res.interval = interval
            elif arg[0] == 'c':
                # 是 count
                try:
                    count = int(arg[1:])
                except ValueError:
                    raise ValueError(f'invalid count: {arg}')
                if count < 0:
                    raise ValueError(f'invalid count: {arg}')
                res.count = count
            else:
                raise ValueError(f'invalid option: {args}')
    else:
        # 是 freq
        freq = freqCode

    rruleFreq: int
    if freq == 'daily':
        rruleFreq = DAILY
    elif freq == 'weekly':
        rruleFreq = WEEKLY
    elif freq == 'monthly':
        rruleFreq = MONTHLY
    elif freq == 'yearly':
        rruleFreq = YEARLY
    else:
        raise ValueError(f'invalid freq: {freq}')
    res.freq = rruleFreq

    return res


def getWeekdayOffset() -> int:
    weekdays = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    return weekdays.index(getSettingsByPath('rrule.wkst'))


def parseBy(byCode: str) -> ByObject:
    bys = ['month', 'weekno', 'yearday', 'monthday', 'day', 'setpos']
    res = ByObject()
    for by in bys:
        index = byCode.find(by)
        if index != -1:
            value = byCode[index + len(by) + 1:byCode.find(']', index)]
            if by != 'day':
                res.__setattr__(f'by{by}', list(map(int, value.split(','))))
            else:
                choices = list(map(int, value.split(',')))
                offset = getWeekdayOffset()
                byweekday = list(map(lambda choice: weekdays[choice - 1 + offset], choices))
                if byweekday[0] is not None and len(byweekday) > 0:
                    res.byweekday = byweekday
                else:
                    raise ValueError(f'invalid byday: {value}')
    return res


def dateSugar(date: str) -> str:
    def repl(match):
        if match.group(0) == 'tdy':
            return datetime.now().astimezone(tz.gettz(getSettingsByPath('rrule.timeZone'))).strftime('%Y/%m/%d')
        elif match.group(0) == 'tmr':
            return (datetime.now() + relativedelta(days=1)).astimezone(
                tz.gettz(getSettingsByPath('rrule.timeZone'))).strftime('%Y/%m/%d')

    date = re.sub(r'tdy|tmr', repl, date)
    return date


def timeSugar(time: str) -> str:
    def repl(match):
        if match.group(0) == 'start' or match.group(0) == 's':
            return ('0:0')
        elif match.group(0) == 'end' or match.group(0) == 'e':
            return ('23:59')
        else:
            return ':'

    time = re.sub(r'start|end|s|e|\.', repl, time)
    return time


def parseTimeCodeLex(timeCode: str) -> TimeCodeLex:
    timeCode = timeCode.strip()
    codes = timeCode.split()  # split 默认忽略连续空格
    if 2 <= len(codes) <= 5:
        [date, time, *options] = codes

        date = dateSugar(date)
        time = timeSugar(time)

        freq = ['daily', 'weekly', 'monthly', 'yearly']
        optionsMark = {
            'timeZone': 0,
            'freq': 0,
            'by': 0,
        }
        timeZone = getSettingsByPath('rrule.timeZone')
        freqCode: str | None = None
        byCode: str | None = None
        while len(options) > 0:
            code: str = options.pop(0)
            if code.find('by[') == 0:
                # 是 by 函数
                optionsMark['by'] += 1
                byCode = code
            elif code in freq or code.split(',')[0] in freq:
                # 是 freq + 参数 或 freq
                optionsMark['freq'] += 1
                freqCode = code
            else:
                # 是时区
                if isValidTimeZone(code):
                    optionsMark['timeZone'] += 1
                    timeZone = code
                else:
                    # 是时区缩写
                    if code in timeZoneAbbrMap:
                        optionsMark['timeZone'] += 1
                        # 从缩写转换为完整的时区，直接选第一个
                        timeZone = list(timeZoneAbbrMap[code])[0]
                    # 是非法内容
                    else:
                        raise ValueError(f'invalid time code options: {code}')

        # 如果有超过两次的
        for key, value in optionsMark.items():
            if value > 1:
                raise ValueError('invalid time code options')

        newTimeCode = f'{date} {time} {timeZone}{f" {freqCode}" if freqCode is not None else ""}{f" {byCode}" if byCode is not None else ""}'

        # 开始解析每个部分
        dateRangeObj = parseDateRange(date)
        timeRangeObj = parseTimeRange(time)
        eventType = EventType.EVENT
        if timeRangeObj.start is None:
            eventType = EventType.TODO

        return TimeCodeLex(eventType, dateRangeObj, timeRangeObj, timeZone, freqCode, byCode, newTimeCode)
    else:
        raise ValueError('time code error')


def getWKST() -> weekday:
    weekStart = getSettingsByPath('rrule.wkst')
    if weekStart == 'MO':
        return MO
    elif weekStart == 'TU':
        return TU
    elif weekStart == 'WE':
        return WE
    elif weekStart == 'TH':
        return TH
    elif weekStart == 'FR':
        return FR
    elif weekStart == 'SA':
        return SA
    elif weekStart == 'SU':
        return SU
    else:
        raise ValueError(f'Unknown wkst: {weekStart}')


def parseTimeCodeSem(
        dateRangeObj: DateRangeObject,
        timeRangeObj: TimeRangeObject,
        timeZone: str,
        freqCode: str | None,
        byCode: str | None) -> TimeCodeSem:
    times: list[TimeRange] = []
    rruleConfig = {}
    dtstart = datetime(**dateRangeObj.dtstart.__dict__)
    rruleConfig['dtstart'] = dtstart
    until: datetime | None = None
    if dateRangeObj.until is not None:
        until = datetime(**dateRangeObj.until.__dict__)
        rruleConfig['until'] = until
    # 默认 daily
    rruleConfig['freq'] = DAILY
    # until is None 时 count: 1
    if until is None:
        rruleConfig['count'] = 1

    if freqCode is not None and dateRangeObj.until is not None:
        freqObj = parseFreq(freqCode)
        rruleConfig = {**rruleConfig, **freqObj.__dict__}
    if byCode is not None and dateRangeObj.until is not None:
        byObj = parseBy(byCode)
        rruleConfig = {**rruleConfig, **byObj.__dict__}
    # wkst
    rruleConfig['wkst'] = getWKST()

    # rrule
    rrule = dateutil.rrule.rrule(**rruleConfig)

    for t in rrule:
        # t 是 UTC 时区的，更改时区，但不改变时间的值
        tAtTimeZone = t.replace(tzinfo=tz.gettz(timeZone))
        start: datetime | None = None
        end = tAtTimeZone.replace(**timeRangeObj.end.__dict__)
        if timeRangeObj.start is not None:
            # 如果 start.hour > end.hour，说明跨天了
            if timeRangeObj.start.hour > timeRangeObj.end.hour:
                end = (tAtTimeZone + relativedelta(days=1)).replace(**timeRangeObj.end.__dict__)
            start = tAtTimeZone.replace(**timeRangeObj.start.__dict__)

        # 转换成 UTC 时区
        start = start.astimezone(tz.gettz('UTC')) if start is not None else start
        end = end.astimezone(tz.gettz('UTC'))

        if end.isoformat() is not None:
            times.append(TimeRange(**{
                **timeRangeObj.__dict__,
                'start': start.isoformat() if start is not None else start,
                'end': end.isoformat()
            }))
        else:
            raise ValueError('The value of end is invalid')

    return TimeCodeSem(times=times, rruleObject=rrule)


def timeCodeParser(timeCode: str) -> TimeCodeParseResult:
    timeCode = timeCode.strip()
    # 去除 \n \t \r 等符号
    timeCode = re.sub(r'\n\t\r', '', timeCode)
    lines = timeCode.split(';')

    eventType: EventType | None = None
    times: list[TimeRange] = []
    rruleObjects: list[rrule] = []
    newTimeCodes: list[str] = []
    for line in lines:
        if len(line) == 0:
            continue
        timeCodeLex = parseTimeCodeLex(line)

        if eventType is not None and eventType != timeCodeLex.eventType:
            raise ValueError('The event type of each line must be the same')
        eventType = timeCodeLex.eventType
        newTimeCodes.append(timeCodeLex.newTimeCode)
        timeCodeSem = parseTimeCodeSem(timeCodeLex.dateRangeObject, timeCodeLex.timeRangeObject, timeCodeLex.timeZone, timeCodeLex.freqCode, timeCodeLex.byCode)
        times.extend(timeCodeSem.times)
        rruleObjects.append(timeCodeSem.rruleObject)

    return TimeCodeParseResult(eventType, times, rruleObjects, newTimeCodes)


def parseTimeCodes(rTimeCodes: str, exTimeCodes: str) -> TimeCodeDao:
    rTimeCodeParseResult = timeCodeParser(rTimeCodes)
    exTimeCodeParseResult = timeCodeParser(exTimeCodes)

    if exTimeCodeParseResult.eventType is not None and rTimeCodeParseResult.eventType != exTimeCodeParseResult.eventType:
        raise ValueError('The event type of each line must be the same')

    rruleStr = ' '.join(map(lambda obj: str(obj), rTimeCodeParseResult.rruleObjects))

    # delete: true, 要去除的时间
    inter = intersection(rTimeCodeParseResult.times, exTimeCodeParseResult.times, lambda a, b: a == b)
    # delete: false, 不要去除的时间
    diff = difference(rTimeCodeParseResult.times, exTimeCodeParseResult.times, lambda a, b: a == b)

    return TimeCodeDao(
        eventType=rTimeCodeParseResult.eventType,
        rTimes=diff,
        exTimes=inter,
        rruleStr=rruleStr,
        rTimeCodes=';'.join(rTimeCodeParseResult.newTimeCodes),
        exTimeCodes=';'.join(exTimeCodeParseResult.newTimeCodes)
    )


if __name__ == '__main__':
    s = 'tdy 123242 tdy'
    print(dateSugar(s))
