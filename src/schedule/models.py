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
    start = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Times(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    schedule_id = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='times')
    start = models.CharField(max_length=255)
    end = models.CharField(max_length=255)
    startMark = models.CharField(max_length=255)
    endMark = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Record(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    schedule_id = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    start = models.CharField(max_length=255)
    end = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
