import json
from datetime import datetime

from dateutil.tz import tz
from django.db import transaction
from django.db.models import QuerySet

from main.models import Base
from setting.models import Setting, toString, fromString
from django_redis import get_redis_connection

from utils.timeZone import isoformat

# 缓存中每个设置是 str
# 数据库中每个设置是 str
# 接口传递的参数是 any 字典的 json 字符串，不是 str 字典的 json 字符串

settingConnection = get_redis_connection('setting')


def getSettings(userId):
    settings = settingConnection.hgetall(userId)
    for key, value in settings.items():
        settings[key] = fromString(key, value)
    return settings


def getSettingByPath(userId: str, path: str):
    value = settingConnection.hget(userId, path)
    return fromString(path, value)


@transaction.atomic
def setSettingByPath(userId: str, path: str, value: any):
    setting = Setting.objects.filter(user_id=userId, key=path).first()
    if setting:
        setting.value = toString(value)  # 接口数据存入数据库, any -> str
        setting.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
        setting.version += 1
        setting.save()
        settingConnection.hset(userId, path, toString(value))  # 接口数据存入缓存, any -> str
        return setting.to_dict()
    return None


@transaction.atomic
def sync(userId, settings, syncAt):
    updated = {
        'settings': [],
    }

    def update(server: Base, client: dict):
        # version 表示数据是从哪个版本开始更新的
        # version 大的覆盖 version 小的
        # version 一样的，updated 大的覆盖 updated 小的
        if server is None:
            return True
        if server.version <= client['version']:
            return True
        if server.updated <= client['updated']:
            return True
        return False

    settingsCache = {}
    for setting in settings:
        settingServer = Setting.objects.filter(user_id=userId, key=setting['key']).first()
        print('update', setting['key'], setting['value'])
        print(update(settingServer, setting))
        if update(settingServer, setting):
            # 更新数据库
            setting['syncAt'] = syncAt
            setting['version'] += 1
            Setting.objects.update_or_create(
                user_id=userId,
                key=setting['key'],
                defaults={
                    'id': f'{userId}:{setting["key"]}',
                    'value': toString(setting['value']),  # 接口数据存入数据库, any -> str
                    'type': setting['type'],
                    'deleted': setting['deleted'],
                    'created': setting['created'],
                    'updated': setting['updated'],
                    'syncAt': setting['syncAt'],
                    'version': setting['version'],
                }
            )
            # 批量更新缓存
            settingsCache[setting['key']] = toString(setting['value'])  # 接口数据存入缓存, any -> str
            updated['settings'].append(setting['key'])

    # 更新 redis
    if len(settingsCache) > 0:
        settingConnection.hmset(userId, settingsCache)

    return updated


def getUnSynced(userId: str, lastSyncAt: str):
    settings = Setting.objects.filter(user_id=userId, updated__gt=lastSyncAt)
    return {
        'settings': list(map(lambda setting: setting.to_dict(), settings)),  # 数据库数据转换为接口数据, json -> any
    }
