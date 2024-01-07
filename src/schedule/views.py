from django.shortcuts import render
from django.http import JsonResponse

from .timeCodeParserTypes import DateUnit


# Create your views here.


def hello(request):
    return JsonResponse(DateUnit().__dict__)


def createSchedule(request):
    pass