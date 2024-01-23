from datetime import datetime

import pytz
from dateutil import tz


def getTimeZoneAbbr(timeZone: str):
    """
    Get the abbreviation of the given time zone.

    :param timeZone: The time zone to get abbreviation.
    :type timeZone: str
    :return: The abbreviation of the given time zone.
    :rtype: str
    """
    now = datetime.now(tz.gettz(timeZone))
    return now.strftime('%Z')


def getTimeZoneAbbrMap():
    """
    Get the abbreviation map of all time zones.

    :return: The abbreviation map of all time zones.
    :rtype: dict[str, list[str]]
    """
    res = {}
    for timezone in pytz.all_timezones:
        abbr = getTimeZoneAbbr(timezone)
        if abbr not in res:
            res[abbr] = set()
        res[abbr].add(timezone)
    return res


def isValidTimeZone(timeZone: str):
    """
    Check if the given time zone is valid.

    :param timeZone: The time zone to check.
    :type timeZone: str
    :return: True if the time zone is valid, False otherwise.
    :rtype: bool
    """
    try:
        tz.gettz(timeZone)
        return True
    except:
        return False


def isoformat(time: datetime) -> str:
    """
    Convert the given time to ISO format.

    :param time: The time to convert.
    :type time: datetime
    :return: The ISO format time.
    :rtype: str
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
