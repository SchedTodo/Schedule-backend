import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .service import FindAllSchedulesConditions
from .timeCodeParserTypes import DateUnit
from . import service


# Create your views here.
def errorHandler(fn: callable):
    def wrapper(*args, **kwargs):
        try:
            res = fn(*args, **kwargs)
            return JsonResponse({'success': True, 'data': res})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return wrapper


def hello(request):
    return JsonResponse(DateUnit().__dict__)


@require_http_methods(["POST"])
def createSchedule(request):
    data = json.loads(request.body)
    name, rTimeCode, comment, exTimeCode = data['name'], data['rTime'], data['comment'], data['exTime']
    return errorHandler(service.createSchedule)(name, rTimeCode, comment, exTimeCode)


@require_http_methods(["POST"])
def updateScheduleById(request):
    data = json.loads(request.body)
    id, name, rTimeCode, comment, exTimeCode = data['id'], data['name'], data['rTime'], data['comment'], data['exTime']
    return errorHandler(service.updateScheduleById)(id, name, rTimeCode, comment, exTimeCode)


@require_http_methods(["POST"])
def findEventsBetween(request):
    data = json.loads(request.body)
    start, end = data['start'], data['end']
    return errorHandler(service.findEventsBetween)(start, end)


@require_http_methods(["POST"])
def findAllTodos(request):
    data = json.loads(request.body)
    return errorHandler(service.findAllTodos)()


@require_http_methods(["POST"])
def findScheduleById(request):
    data = json.loads(request.body)
    id = data['id']
    return errorHandler(service.findScheduleById)(id)


@require_http_methods(["POST"])
def findTimesByScheduleId(request):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return errorHandler(service.findTimesByScheduleId)(scheduleId)


@require_http_methods(["POST"])
def findRecordsByScheduleId(request):
    data = json.loads(request.body)
    scheduleId = data['scheduleId']
    return errorHandler(service.findRecordsByScheduleId)(scheduleId)


@require_http_methods(["POST"])
def deleteScheduleById(request):
    data = json.loads(request.body)
    id = data['id']
    return errorHandler(service.deleteScheduleById)(id)


@require_http_methods(["POST"])
def deleteTimeByIds(request):
    data = json.loads(request.body)
    ids = data['ids']
    return errorHandler(service.deleteTimeByIds)(ids)


@require_http_methods(["POST"])
def updateTimeCommentById(request):
    data = json.loads(request.body)
    id, comment = data['id'], data['comment']
    return errorHandler(service.updateTimeCommentById)(id, comment)


@require_http_methods(["POST"])
def findAllSchedules(request):
    data = json.loads(request.body)
    conditions, page, pageSize = data['conditions'], data['page'], data['pageSize']
    conditions = FindAllSchedulesConditions(conditions)
    return errorHandler(service.findAllSchedules)(conditions, page, pageSize)


@require_http_methods(["POST"])
def updateDoneById(request):
    data = json.loads(request.body)
    id, done = data['id'], data['done']
    return errorHandler(service.updateDoneById)(id, done)


@require_http_methods(["POST"])
def updateStarById(request):
    data = json.loads(request.body)
    id, star = data['id'], data['star']
    return errorHandler(service.updateStarById)(id, star)


@require_http_methods(["POST"])
def createRecord(request):
    data = json.loads(request.body)
    scheduleId, startTime, endTime = data['scheduleId'], data['startTime'], data['endTime']
    return errorHandler(service.createRecord)(scheduleId, startTime, endTime)

