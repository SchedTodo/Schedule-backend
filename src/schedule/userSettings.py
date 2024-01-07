def getSettingsByPath(path):
    if path == 'rrule.timeZone':
        return 'America/Chicago'
    elif path == 'rrule.wkst':
        return 'MO'
    elif path == 'preferences.startTime.hour':
        return 4
    elif path == 'preferences.startTime.minute':
        return 0