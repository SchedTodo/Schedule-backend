from datetime import datetime

from django.test import TestCase
from .timeCodeParser import parseDateRange
from .timeCodeParserTypes import (EventType, DateRangeObject, TimeRangeObject, TimeRange, FreqObject, ByObject,
                                  TimeCodeLex, TimeCodeSem, TimeCodeParseResult, TimeCodeDao, DateUnit)


# Create your tests here.
class ParseDateTest(TestCase):
    def test_parseDate(self):
        self.assertEqual(parseDateRange('2021/10/1'), DateRangeObject(DateUnit(2021, 10, 1)))

    def test_parseDateSugar(self):
        print(parseDateRange('2021/10/1-11/1'))
        self.assertEqual(parseDateRange('2021/10/1-11/1'), DateRangeObject(DateUnit(2021, 10, 1), DateUnit(2021, 11, 1)))
        year = datetime.now().year
        if datetime.now().month >= 10 and datetime.now().day >= 1:
            year += 1
        self.assertEqual(parseDateRange('10/1-25'), DateRangeObject(DateUnit(year, 10, 1), DateUnit(year, 10, 25)))
        self.assertEqual(parseDateRange('10/1'), DateRangeObject(DateUnit(year, 10, 1)))
