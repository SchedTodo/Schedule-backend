import json

from django.shortcuts import render

from main.decorators import errorHandler, checkToken
from django.views.decorators.http import require_http_methods
from . import service

# Create your views here.


@errorHandler
@checkToken
@require_http_methods(['POST'])
def getSettings(request, userId):
    return service.getSettings(userId)


@errorHandler
@checkToken
@require_http_methods(['POST'])
def setSettings(request, userId):
    data = json.loads(request.body)
    settings = data['settings']
    return service.setSettings(userId, settings)


@errorHandler
@checkToken
@require_http_methods(['POST'])
def getSettingByPath(request, userId):
    data = json.loads(request.body)
    path = data['path']
    return service.getSettingByPath(userId, path)


@errorHandler
@checkToken
@require_http_methods(['POST'])
def setSettingByPath(request, userId):
    """
    @deprecated
    """
    data = json.loads(request.body)
    path, value = data['path'], data['value']
    return service.setSettingByPath(userId, path, value)


@errorHandler
@checkToken
@require_http_methods(['POST'])
def sync(request, userId):
    data = json.loads(request.body)
    settings = data['settings']
    syncAt = data['syncAt']
    print(settings, syncAt)
    return service.sync(userId, settings, syncAt)


@errorHandler
@checkToken
@require_http_methods(['POST'])
def getUnSynced(request, userId):
    data = json.loads(request.body)
    lastSyncAt = data['lastSyncAt']
    return service.getUnSynced(userId, lastSyncAt)
