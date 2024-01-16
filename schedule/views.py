import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from main.decorators import errorHandler, checkToken
from .service import FindAllSchedulesConditions
from .timeCodeParserTypes import DateUnit
from . import service


# Create your views here.
@require_http_methods(["POST"])
@errorHandler
@checkToken
def createSchedule(request):
    data = json.loads(request.body)
    name, rTimeCode, comment, exTimeCode = data['name'], data['rTime'], data['comment'], data['exTime']
    return service.createSchedule(name, rTimeCode, comment, exTimeCode)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def updateScheduleById(request):
    data = json.loads(request.body)
    id, name, rTimeCode, comment, exTimeCode = data['id'], data['name'], data['rTime'], data['comment'], data['exTime']
    return service.updateScheduleById(id, name, rTimeCode, comment, exTimeCode)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findEventsBetween(request):
    data = json.loads(request.body)
    start, end = data['start'], data['end']
    return service.findEventsBetween(start, end)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findAllTodos(request):
    return service.findAllTodos()


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findScheduleById(request):
    data = json.loads(request.body)
    id = data['id']
    return service.findScheduleById(id)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findTimesByScheduleId(request):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return service.findTimesByScheduleId(scheduleId)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findRecordsByScheduleId(request):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return service.findRecordsByScheduleId(scheduleId)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def deleteScheduleById(request):
    data = json.loads(request.body)
    id = data['id']
    return service.deleteScheduleById(id)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def deleteTimeByIds(request):
    data = json.loads(request.body)
    ids = data['ids']
    return service.deleteTimeByIds(ids)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def updateTimeCommentById(request):
    data = json.loads(request.body)
    id, comment = data['id'], data['comment']
    return service.updateTimeCommentById(id, comment)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def findAllSchedules(request):
    data = json.loads(request.body)
    conditions, page, pageSize = data['conditions'], data['page'], data['pageSize']
    conditions = FindAllSchedulesConditions(conditions)
    return service.findAllSchedules(conditions, page, pageSize)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def updateDoneById(request):
    data = json.loads(request.body)
    id, done = data['id'], data['done']
    return service.updateDoneById(id, done)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def updateStarById(request):
    data = json.loads(request.body)
    id, star = data['id'], data['star']
    return service.updateStarById(id, star)


@require_http_methods(["POST"])
@errorHandler
@checkToken
def createRecord(request):
    data = json.loads(request.body)
    scheduleId, startTime, endTime = data['scheduleId'], data['startTime'], data['endTime']
    return service.createRecord(scheduleId, startTime, endTime)

