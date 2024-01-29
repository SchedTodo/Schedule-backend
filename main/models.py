from django.db import models


class Base(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    deleted = models.BooleanField(default=False)
    created = models.CharField(max_length=255)
    updated = models.CharField(max_length=255)
    syncAt = models.CharField(max_length=255, null=True)
    version = models.IntegerField(default=0)

    class Meta:
        abstract = True
