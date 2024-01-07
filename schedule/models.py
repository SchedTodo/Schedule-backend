from django.db import models


class Schedule(models.Model):
    class ScheduleType(models.TextChoices):
        EVENT = 'event'
        TODO = 'todo'

    id = models.CharField(primary_key=True, max_length=255)
    type = models.CharField(choices=ScheduleType.choices, max_length=255)
    name = models.TextField()
    rrules = models.TextField()
    rTimeCode = models.TextField()
    exTimeCode = models.TextField()
    comment = models.TextField()
    star = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
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
        }


class Time(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='times')
    start = models.CharField(max_length=255, null=True)
    end = models.CharField(max_length=255)
    startMark = models.CharField(max_length=255)
    endMark = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, default='')
    done = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.start}-{self.end}'

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'start': self.start,
            'end': self.end,
            'startMark': self.startMark,
            'endMark': self.endMark,
            'comment': self.comment,
            'done': self.done,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
        }


class Record(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='record')
    start = models.CharField(max_length=255)
    end = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.start}-{self.end}'

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'start': self.start,
            'end': self.end,
            'deleted': self.deleted,
            'created': self.created,
            'updated': self.updated,
        }
