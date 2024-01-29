import json
from datetime import datetime

from dateutil.tz import tz
from django.db import models
from main.models import Base
from utils.timeZone import isoformat


class SettingType(models.TextChoices):
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'


settingsDict = {
    'rrule.timeZone': (SettingType.STRING, ''),
    'rrule.wkst': (SettingType.STRING, 'MO'),
    'alarm.todo.enable': (SettingType.BOOLEAN, True),
    'alarm.todo.before.hour': (SettingType.NUMBER, 0),
    'alarm.todo.before.minute': (SettingType.NUMBER, 5),
    'alarm.event.enable': (SettingType.BOOLEAN, True),
    'alarm.event.before.hour': (SettingType.NUMBER, 0),
    'alarm.event.before.minute': (SettingType.NUMBER, 5),
    'preferences.priority': (SettingType.STRING, 'month'),
    'preferences.days': (SettingType.NUMBER, 5),
    'preferences.startTime.hour': (SettingType.NUMBER, 0),
    'preferences.startTime.minute': (SettingType.NUMBER, 0),
    'preferences.openAtLogin': (SettingType.BOOLEAN, False),
    'pomodoro.focus.hour': (SettingType.NUMBER, 0),
    'pomodoro.focus.minute': (SettingType.NUMBER, 25),
    'pomodoro.smallBreak.hour': (SettingType.NUMBER, 0),
    'pomodoro.smallBreak.minute': (SettingType.NUMBER, 5),
    'pomodoro.bigBreak.hour': (SettingType.NUMBER, 0),
    'pomodoro.bigBreak.minute': (SettingType.NUMBER, 20),
}


def toString(value):
    """
    将接口数据转换为 redis 需要的 str
    """
    if type(value) is str:
        return value
    return json.dumps(value)


def fromString(path, value):
    """
    将 redis 中的 value 转换为对应的类型
    """
    if settingsDict[path][0] == 'number':
        return int(value)
    if settingsDict[path][0] == 'boolean':
        return value == 'true'
    return value


# Create your models here.
class Setting(Base):
    user = models.ForeignKey('user.ScheduleUser', on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=255)
    value = models.TextField()
    type = models.CharField(choices=SettingType.choices, max_length=255)

    def __str__(self):
        return self.key

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'key': self.key,
            'value': fromString(self.key, self.value),
            'type': self.type,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
            'syncAt': self.syncAt,
            'version': self.version,
        }
