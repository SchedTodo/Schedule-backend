from django.shortcuts import render
from django.http import JsonResponse

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


def createSchedule(request):
    name, rTimeCode, comment, exTimeCode = request.POST['name'], request.POST['rTimeCode'], request.POST['comment'], request.POST['exTimeCode']
    return errorHandler(service.createSchedule)(name, rTimeCode, comment, exTimeCode)


def updateScheduleById(request):
    id, name, rTimeCode, comment, exTimeCode = request.POST['id'], request.POST['name'], request.POST['rTimeCode'], request.POST['comment'], request.POST['exTimeCode']
    return errorHandler(service.updateScheduleById)(id, name, rTimeCode, comment, exTimeCode)


def findEventsBetween(request):
    start, end = request.POST['start'], request.POST['end']
    return errorHandler(service.findEventsBetween)(start, end)


def findAllTodos(request):
    return errorHandler(service.findAllTodos)()


def findScheduleById(request):
    id = request.POST['id']
    return errorHandler(service.findScheduleById)(id)


def findTimesByScheduleId(request):
    scheduleId = request.POST['scheduleId']
    return errorHandler(service.findTimesByScheduleId)(scheduleId)


def findRecordsByScheduleId(request):
    scheduleId = request.POST['scheduleId']
    return errorHandler(service.findRecordsByScheduleId)(scheduleId)


def deleteScheduleById(request):
    id = request.POST['id']
    return errorHandler(service.deleteScheduleById)(id)


def deleteTimeByIds(request):
    ids = request.POST['ids']
    return errorHandler(service.deleteTimeByIds)(ids)


def updateTimeCommentById(request):
    id, comment = request.POST['id'], request.POST['comment']
    return errorHandler(service.updateTimeCommentById)(id, comment)


def findAllSchedules(request):
    conditions, page, pageSize = request.POST['conditions'], request.POST['page'], request.POST['pageSize']
    return errorHandler(service.findAllSchedules)()


def updateDoneById(request):
    id, done = request.POST['id'], request.POST['done']
    return errorHandler(service.updateDoneById)(id, done)


def updateStarById(request):
    id, star = request.POST['id'], request.POST['star']
    return errorHandler(service.updateStarById)(id, star)


def createRecord(request):
    scheduleId, startTime, endTime = request.POST['scheduleId'], request.POST['startTime'], request.POST['endTime']
    return errorHandler(service.createRecord)(scheduleId, startTime, endTime)

