import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from main.decorators import errorHandler, checkToken
from .service import FindAllSchedulesConditions
from .timeCodeParserTypes import DateUnit
from . import service


# Create your views here.
@errorHandler
@checkToken
@require_http_methods(["POST"])
def createSchedule(request, userId):
    data = json.loads(request.body)
    name, rTimeCode, comment, exTimeCode = data['name'], data['rTime'], data['comment'], data['exTime']
    return service.createSchedule(userId, name, rTimeCode, comment, exTimeCode)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def updateScheduleById(request, userId):
    data = json.loads(request.body)
    id, name, rTimeCode, comment, exTimeCode = data['id'], data['name'], data['rTime'], data['comment'], data['exTime']
    return service.updateScheduleById(id, userId, name, rTimeCode, comment, exTimeCode)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findEventsBetween(request, userId):
    data = json.loads(request.body)
    start, end = data['start'], data['end']
    return service.findEventsBetween(userId, start, end)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findAllTodos(request, userId):
    return service.findAllTodos(userId)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findScheduleById(request, userId):
    data = json.loads(request.body)
    id = data['id']
    return service.findScheduleById(id, userId)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findTimesByScheduleId(request, userId):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return service.findTimesByScheduleId(scheduleId, userId)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findRecordsByScheduleId(request, userId):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return service.findRecordsByScheduleId(scheduleId, userId)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def deleteScheduleById(request, userId):
    data = json.loads(request.body)
    id = data['id']
    return service.deleteScheduleById(id, userId)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def deleteTimeByIds(request, userId):
    data = json.loads(request.body)
    ids = data['ids']
    return service.deleteTimeByIds(userId, ids)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def updateTimeCommentById(request, userId):
    data = json.loads(request.body)
    id, comment = data['id'], data['comment']
    return service.updateTimeCommentById(userId, id, comment)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def findAllSchedules(request, userId):
    data = json.loads(request.body)
    conditions, page, pageSize = data['conditions'], data['page'], data['pageSize']
    conditions = FindAllSchedulesConditions(conditions)
    return service.findAllSchedules(userId, conditions, page, pageSize)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def updateDoneById(request, userId):
    data = json.loads(request.body)
    id, done = data['id'], data['done']
    return service.updateDoneById(userId, id, done)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def updateStarById(request, userId):
    data = json.loads(request.body)
    id, star = data['id'], data['star']
    return service.updateStarById(userId, id, star)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def createRecord(request, userId):
    data = json.loads(request.body)
    scheduleId, startTime, endTime = data['scheduleId'], data['startTime'], data['endTime']
    return service.createRecord(scheduleId, userId, startTime, endTime)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def sync(request, userId):
    data = json.loads(request.body)
    schedules, times, records, syncAt = data['schedules'], data['times'], data['records'], data['syncAt']
    return service.sync(userId, schedules, times, records, syncAt)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def getUnSynced(request, userId):
    data = json.loads(request.body)
    lastSyncAt = data['lastSyncAt']
    return service.getUnSynced(userId, lastSyncAt)
