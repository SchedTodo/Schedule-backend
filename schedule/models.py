from django.db import models
from main.models import Base
from user.models import ScheduleUser


class Schedule(Base):
    class ScheduleType(models.TextChoices):
        EVENT = 'event'
        TODO = 'todo'

    user = models.ForeignKey(ScheduleUser, on_delete=models.CASCADE, related_name='schedules')
    type = models.CharField(choices=ScheduleType.choices, max_length=255)
    name = models.TextField()
    rrules = models.TextField()
    rTimeCode = models.TextField()
    exTimeCode = models.TextField()
    comment = models.TextField()
    star = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'type': self.type,
            'name': self.name,
            'rrules': self.rrules,
            'rTimeCode': self.rTimeCode,
            'exTimeCode': self.exTimeCode,
            'comment': self.comment,
            'star': self.star,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
            'syncAt': self.syncAt,
            'version': self.version,
        }


class Time(Base):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='times')
    excluded = models.BooleanField(default=False)
    start = models.CharField(max_length=255, null=True)
    end = models.CharField(max_length=255)
    startMark = models.CharField(max_length=255)
    endMark = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, default='')
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.start}-{self.end}'

    def to_dict(self):
        return {
            'id': self.id,
            'scheduleId': self.schedule_id,
            'excluded': self.excluded,
            'start': self.start,
            'end': self.end,
            'startMark': self.startMark,
            'endMark': self.endMark,
            'comment': self.comment,
            'done': self.done,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
            'syncAt': self.syncAt,
            'version': self.version,
        }


class Record(Base):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='record')
    start = models.CharField(max_length=255)
    end = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.start}-{self.end}'

    def to_dict(self):
        return {
            'id': self.id,
            'scheduleId': self.schedule_id,
            'start': self.start,
            'end': self.end,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
            'syncAt': self.syncAt,
            'version': self.version,
        }
