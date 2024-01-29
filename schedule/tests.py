from datetime import datetime

from dateutil.rrule import rrule, DAILY, MONTHLY, YEARLY, WEEKLY, MO, TU, WE, TH, FR, SA, SU, weekday
from dateutil.tz import tz
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from schedule.timeCodeParser import parseDateRange, parseTimeRange, parseFreq, parseBy, parseTimeCodes
from schedule.timeCodeParserTypes import (EventType, DateRangeObject, TimeRangeObject, TimeUnit, TimeRange,
                                              FreqObject, ByObject,
                                              TimeCodeLex, TimeCodeSem, TimeCodeParseResult, TimeCodeDao, DateUnit)
from schedule.userSettings import getSettingByPath


# Create your tests here.
class ParseDateTest(TestCase):
    def test_parseDate(self):
        self.assertEqual(parseDateRange('2021/10/1'), DateRangeObject(dtstart=DateUnit(2021, 10, 1)))

    def test_parseDateRange(self):
        self.assertEqual(parseDateRange('2021/10/1-2021/10/2'),
                         DateRangeObject(dtstart=DateUnit(2021, 10, 1), until=DateUnit(2021, 10, 2)))

    def test_parseDateSugar(self):
        self.assertEqual(parseDateRange('2021/10/1-11/1'),
                         DateRangeObject(dtstart=DateUnit(2021, 10, 1), until=DateUnit(2021, 11, 1)))
        year = datetime.now().year
        if datetime.now().month >= 10 and datetime.now().day >= 1:
            year += 1
        self.assertEqual(parseDateRange('10/1-25'),
                         DateRangeObject(dtstart=DateUnit(year, 10, 1), until=DateUnit(year, 10, 25)))
        self.assertEqual(parseDateRange('10/1'), DateRangeObject(dtstart=DateUnit(year, 10, 1)))


class ParseTimeTest(TestCase):
    def test_parseTime(self):
        self.assertEqual(parseTimeRange('20:30'), TimeRangeObject(end=TimeUnit(20, 30), startMark='11', endMark='11'))

    def test_parseTimeRange(self):
        self.assertEqual(parseTimeRange('20:30-21:30'),
                         TimeRangeObject(start=TimeUnit(20, 30), end=TimeUnit(21, 30), startMark='11', endMark='11'))

    def test_parseTimeRangeStartUnknown(self):
        self.assertEqual(parseTimeRange('?:?-21:30'),
                         TimeRangeObject(start=TimeUnit(0, 0), end=TimeUnit(21, 30), startMark='00', endMark='11'))

    def test_parseTimeRangeStartHourUnknown(self):
        self.assertRaises(Exception, parseTimeRange, '?:30-21:30')

    def test_parseTimeRangeStartMinUnknown(self):
        self.assertEqual(parseTimeRange('20:?-21:00'),
                         TimeRangeObject(start=TimeUnit(20, 0), end=TimeUnit(21, 0), startMark='10', endMark='11'))

    def test_parseTimeRangeEndUnknown(self):
        self.assertEqual(parseTimeRange('20:30-?:?'),
                         TimeRangeObject(start=TimeUnit(20, 30), end=TimeUnit(0, 0), startMark='11', endMark='00'))

    def test_parseTimeRangeEndHourUnknown(self):
        self.assertRaises(Exception, parseTimeRange, '20:30-?:30')

    def test_parseTimeRangeEndMinUnknown(self):
        self.assertEqual(parseTimeRange('20:30-21:?'),
                         TimeRangeObject(start=TimeUnit(20, 30), end=TimeUnit(21, 0), startMark='11', endMark='10'))

    def test_parseTimeRangeStartEndHourUnknown(self):
        self.assertRaises(Exception, parseTimeRange, '?:30-?:30')

    def test_parseTimeRangeStartEndMinUnknown(self):
        self.assertEqual(parseTimeRange('20:?-21:?'),
                         TimeRangeObject(start=TimeUnit(20, 0), end=TimeUnit(21, 0), startMark='10', endMark='10'))

    def test_parseTimeRangeAllUnknown(self):
        self.assertRaises(Exception, parseTimeRange, '?:?-?:?')


class ParseFreqTest(TestCase):
    def test_parseFreq(self):
        self.assertEqual(parseFreq('daily'), FreqObject(freq=DAILY))

    def test_parseFreqWithInterval(self):
        self.assertEqual(parseFreq('weekly,i2'), FreqObject(freq=WEEKLY, interval=2))

    def test_parseFreqWithCount(self):
        self.assertEqual(parseFreq('monthly,c2'), FreqObject(freq=MONTHLY, count=2))

    def test_parseFreqWithIntervalAndCount(self):
        self.assertEqual(parseFreq('daily,i10,c20'), FreqObject(freq=DAILY, interval=10, count=20))
        self.assertEqual(parseFreq('yearly,c0,i1'), FreqObject(freq=YEARLY, interval=1, count=0))


class ParseByTest(TestCase):
    def test_parseBy(self):
        self.assertEqual(parseBy('by[day[1,2,3]]'), ByObject(byweekday=[MO, TU, WE]))

    def test_parseByDayMonth(self):
        self.assertEqual(parseBy('by[day[1,2,3],month[1,2,3]]'), ByObject(byweekday=[MO, TU, WE], bymonth=[1, 2, 3]))


class ParseTimeCodeTest(TestCase):
    def test_parseTimeCode(self):
        times = parseTimeCodes('2023/7/10 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')

    def test_parseTimeCodeSpaces(self):
        times = parseTimeCodes('2023/7/10    22:00    America/Los_Angeles;  ', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')

    def test_parseTimeCodeAbbr(self):
        times = parseTimeCodes('2023/7/10 22:00 CST;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Chicago'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')

    def test_paseTimeCodeDateSugar1(self):
        times = parseTimeCodes('tdy 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), datetime.now().strftime('%Y/%m/%d') + ' 22:00')

    def test_paseTimeCodeDateSugar2(self):
        times = parseTimeCodes('tmr 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), (datetime.now() + relativedelta(days=1)).strftime('%Y/%m/%d') + ' 22:00')

    def test_paseTimeCodeDateSugar3(self):
        times = parseTimeCodes('7/10 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            if datetime.now().month > 7 or (datetime.now().month == 7 and datetime.now().day > 10):
                self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'{datetime.now().year + 1}/07/10 22:00')
            else:
                self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'{datetime.now().year}/07/10 22:00')

    def test_paseTimeCodeDateSugar4(self):
        times = parseTimeCodes('7/20-30 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 11)
        day = 20
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            if datetime.now().month > 7 or (datetime.now().month == 7 and datetime.now().day > day):
                self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'{datetime.now().year + 1}/07/{day} 22:00')
            else:
                self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'{datetime.now().year}/07/{day} 22:00')
            day += 1

    def test_paseTimeCodeTimeZoneSugar1(self):
        times = parseTimeCodes('2023/7/10 22:00;', '').rTimes
        self.assertEqual(len(times), 1)
        timeZone = getSettingByPath('rrule.timeZone')
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')

    def test_paseTimeCodeTimeZoneSugar2(self):
        times = parseTimeCodes('2023/7/10-2023/7/25 22:00 by[day[1]];', '').rTimes
        self.assertEqual(len(times), 3)
        timeZone = getSettingByPath('rrule.timeZone')
        day = 10
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{day} 22:00')
            day += 7

    def test_paseTimeCodeDateRangeSugar1(self):
        times = parseTimeCodes('2023/7/10-8/10 22:00 by[day[1]];', '').rTimes
        self.assertEqual(len(times), 5)
        timeZone = getSettingByPath('rrule.timeZone')
        month = 7
        day = 10
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/{str(month).zfill(2)}/{str(day).zfill(2)} 22:00')
            day += 7
            if day > 31:
                day %= 31
                month += 1

    def test_paseTimeCodeDateRangeSugar2(self):
        times = parseTimeCodes('2023/7/10-31 22:00 by[day[1]];', '').rTimes
        self.assertEqual(len(times), 4)
        timeZone = getSettingByPath('rrule.timeZone')
        day = 10
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 7

    def test_paseTimeCodeTimeRangeSugar1(self):
        times = parseTimeCodes('2023/7/10 22-23 by[day[1]];', '').rTimes
        self.assertEqual(len(times), 1)
        timeZone = getSettingByPath('rrule.timeZone')
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz(timeZone))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:00')

    def test_paseTimeCodeTimeRangeSugar2(self):
        times = parseTimeCodes('2023/7/10 22-23:30 by[day[1]];', '').rTimes
        self.assertEqual(len(times), 1)
        timeZone = getSettingByPath('rrule.timeZone')
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz(timeZone))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz(timeZone))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:30')

    def test_paseTimeCodeTimeRangeSugar3(self):
        times = parseTimeCodes('2023/7/10 22-?:? by[day[1]];', '').rTimes
        self.assertEqual(len(times), 1)
        timeZone = getSettingByPath('rrule.timeZone')
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz(timeZone))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')
            self.assertEqual(time.endMark, '00')

    def test_paseTimeCodeTimeRangeSugar4(self):
        times = parseTimeCodes('2023/7/10 end America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:59')

    def test_paseTimeCodeTimeRangeSugar5(self):
        times = parseTimeCodes('2023/7/10 22:30-e America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:30')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:59')

    def test_paseTimeCodeTimeRangeSugar6(self):
        times = parseTimeCodes('2023/7/10 s-2:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 00:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 02:00')

    def test_paseTimeCodeTimeRangeSugar7(self):
        times = parseTimeCodes('2023/7/10 start-end America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 00:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:59')

    def test_paseTimeCodeTimeRangeSugar8(self):
        times = parseTimeCodes('2023/7/10 22.30-23.0 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:30')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:00')

    def test_paseTimeCodeTimeRangeSugar9(self):
        times = parseTimeCodes('2023/7/10 22:-: America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 22:00')
            self.assertEqual(time.startMark, '10')
            self.assertEqual(time.endMark, '00')

    def test_parseTimeCodeDateRangeTime(self):
        times = parseTimeCodes('2023/7/10-2023/7/11 22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 2)
        day = 10
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCodeDateTimeRange(self):
        times = parseTimeCodes('2023/7/10 21:00-22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 1)
        day = 10
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCodeDateRangeTimeRange(self):
        times = parseTimeCodes('2023/7/10-2023/7/12 21:00-22:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 3)
        day = 10
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCodeDateRangeTimeRangeFreq(self):
        times = parseTimeCodes('2023/7/10-2023/7/15 21:00-22:00 America/Los_Angeles daily,i2;', '')
        self.assertEqual(len(times.rTimes), 3)
        day = 10
        for time in times.rTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 2

    def test_parseTimeCodeDateRangeTimeRangeFreq2(self):
        times = parseTimeCodes('2023/7/10-2023/7/15 21:00-22:00 America/Los_Angeles daily,i2,c2;', '')
        self.assertEqual(len(times.rTimes), 2)
        day = 10
        for time in times.rTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 2

    def test_parseTimeCodeDateRangeTimeRangeByDay(self):
        times = parseTimeCodes('2023/7/10-2023/7/15 21:00-22:00 America/Los_Angeles by[day[2,3]];', '')
        self.assertEqual(len(times.rTimes), 2)
        day = 11
        for time in times.rTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCodeDateRangeTimeRangeByMonth(self):
        times = parseTimeCodes('2023/7/10-2023/8/12 21:00-22:00 America/Los_Angeles by[month[6,7]];', '')
        self.assertEqual(len(times.rTimes), 22)
        day = 10
        for time in times.rTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCodeNextDay(self):
        times = parseTimeCodes('2023/7/10 23:00-01:00 CST;', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Chicago'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Chicago'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), '2023/07/10 23:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/07/11 01:00')

    def test_parseTimeCodeDateRangeTimeRange_RTime(self):
        times = parseTimeCodes('2023/7/10-2023/7/11 21:00-22:00 America/Los_Angeles; 2023/7/10-2023/7/11 15:00-16:00 America/Los_Angeles;', '').rTimes
        self.assertEqual(len(times), 4)
        day = 10
        for i in range(2):
            time = times[i]
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day + i).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day + i).zfill(2)} 22:00')
        for i in range(2, 4):
            time = times[i]
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day + i - 2).zfill(2)} 15:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day + i - 2).zfill(2)} 16:00')

    def test_parseTimeCodeDateRangeTimeRange_ExTime(self):
        res = parseTimeCodes('2023/7/10-2023/7/12 21:00-22:00 America/Los_Angeles;', '2023/7/11 21:00-22:00 America/Los_Angeles;')
        rTimes = res.rTimes
        exTimes = res.exTimes
        self.assertEqual(len(rTimes), 2)
        self.assertEqual(len(exTimes), 1)
        day = 10
        for time in rTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 2
        day = 11
        for time in exTimes:
            tStart = datetime.fromisoformat(time.start).astimezone(tz.gettz('America/Los_Angeles'))
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tStart.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 21:00')
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), f'2023/07/{str(day).zfill(2)} 22:00')
            day += 1

    def test_parseTimeCode_nextDay(self):
        times = parseTimeCodes('2023/8/9 23:59 America/Los_Angeles;\n', '').rTimes
        self.assertEqual(len(times), 1)
        for time in times:
            tEnd = datetime.fromisoformat(time.end).astimezone(tz.gettz('America/Los_Angeles'))
            self.assertEqual(tEnd.strftime('%Y/%m/%d %H:%M'), '2023/08/09 23:59')

    def test_parseTimeCodeInvalid(self):
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30/1 22:00 America/Chicago', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30 22:00:00 America/Chicago', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30 ?:20 America/Chicago', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago dly;', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago dly,i2,c2;', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago daily,ia;', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago daily,i2,ca;', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago daily,i2,c2 monthly.i2;', '')
        self.assertRaises(IndexError, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago by[day[8]];', '')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00 America/Chicago;', '2023/11/30-12/21 22:00-23:00 America/Chicago;')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00-23:00 America/Chicago;', '2023/11/30-12/21 22:00 America/Chicago;')
        self.assertRaises(Exception, parseTimeCodes, '', '2023/11/30-12/21 22:00-23:00 America/Chicago;')
        self.assertRaises(Exception, parseTimeCodes, '2023/11/30-12/21 22:00-23:00 America/Chicago; 2023/11/30-12/21 22:00 America/Chicago;', '')


class TimeTest(TestCase):
    def test_replaceTimeZone(self):
        t = datetime.fromisoformat('2023-07-10T21:00:00.000Z')
        timeZone = 'America/Chicago'
        tAtTimeZone = t.replace(tzinfo=tz.gettz(timeZone))
        self.assertEqual(tAtTimeZone.isoformat(), '2023-07-10T21:00:00-05:00')

    def test_relativeDelta(self):
        t = datetime.fromisoformat('2023-07-10T21:00:00.000Z')
        tDelta1 = t + relativedelta(days=1)
        self.assertEqual(tDelta1.isoformat(), '2023-07-11T21:00:00+00:00')
        tDelta2 = t + relativedelta(day=11)
        self.assertEqual(tDelta2.isoformat(), '2023-07-11T21:00:00+00:00')
        tDelta3 = t + relativedelta(hour=10, minute=30)
        self.assertEqual(tDelta3.isoformat(), '2023-07-10T10:30:00+00:00')