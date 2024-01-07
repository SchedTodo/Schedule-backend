from django.contrib import admin

# Register your models here.

from .models import Schedule, Time, Record

admin.site.register(Schedule)
admin.site.register(Time)
admin.site.register(Record)
