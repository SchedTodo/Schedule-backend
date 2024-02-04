import uuid
from copy import deepcopy
from datetime import datetime
from django.core.paginator import Paginator

from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import F

from schedule.models import Schedule, Time, Record, Base
from schedule.timeCodeParser import parseTimeCodes
from schedule.timeCodeParserTypes import TimeRange, EventType
from setting.service import getSettingByPath
from utils.utils import difference, union
from utils.timeZone import isoformat
from utils.vo import EventBriefVO, TodoBriefVO, ScheduleBriefVO


@transaction.atomic
def createSchedule(userId: str, name: str, timeCodes: str, comment: str, exTimeCodes: str):
    parseRes = parseTimeCodes(timeCodes, exTimeCodes)
    eventType, rTimes, exTimes, rruleStr, code, exCode = parseRes.eventType, parseRes.rTimes, parseRes.exTimes, parseRes.rruleStr, parseRes.rTimeCodes, parseRes.exTimeCodes

    schedule = Schedule(id=uuid.uuid4().hex, user_id=userId, type=eventType, name=name, rrules=rruleStr, rTimeCode=code,
                        exTimeCode=exCode, comment=comment,
                        created=isoformat(datetime.now().astimezone(tz.gettz('UTC'))),
                        updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
    schedule.save()

    allTimes = {
        'rTimes': rTimes,
        'exTimes': exTimes
    }

    for key, value in allTimes.items():
        for time in value:
            time = Time(id=uuid.uuid4().hex, schedule_id=schedule.id,
                        excluded=False if key == 'rTimes' else True,
                        start=time.start, end=time.end,
                        startMark=time.startMark,
                        endMark=time.endMark, done=False,
                        created=isoformat(datetime.now().astimezone(tz.gettz('UTC'))),
                        updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
            time.save()

    return schedule.to_dict()


@transaction.atomic
def updateScheduleById(id: str, userId: str, name: str, timeCodes: str, comment: str, exTimeCodes: str):
    oldSchedule = Schedule.objects.get(id=id, user_id=userId)

    if oldSchedule.deleted:
        raise Exception('try to update a deleted schedule')

    parseRes = parseTimeCodes(timeCodes, exTimeCodes)
    eventType, rTimes, exTimes, rruleStr, code, exCode = parseRes.eventType, parseRes.rTimes, parseRes.exTimes, parseRes.rruleStr, parseRes.rTimeCodes, parseRes.exTimeCodes

    if oldSchedule.type != eventType:
        raise Exception('try to change schedule type')

    schedule = deepcopy(oldSchedule)
    schedule.name = name
    schedule.rrules = rruleStr
    schedule.rTimeCode = code
    schedule.exTimeCode = exCode
    schedule.comment = comment
    schedule.version += 1
    schedule.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    schedule.save()

    # 如果时间片没有变化，直接返回
    if oldSchedule.rTimeCode == code and oldSchedule.exTimeCode == exCode:
        return oldSchedule.to_dict()

    # 获取所有和该 Schedule 相关的时间片, Schedule 已经限定了 user_id，所以不需要再限定
    times = Time.objects.filter(schedule__id=id)

    def equal(time1: TimeRange | Time, time2: TimeRange | Time):
        """
        两个时间片相等的条件
        """
        if time1.start is not None and time1.end is not None:
            if datetime.fromisoformat(time1.start) != datetime.fromisoformat(time2.start):
                return False
        if datetime.fromisoformat(time1.end) != datetime.fromisoformat(time2.end):
            return False
        if time1.startMark != time2.startMark:
            return False
        if time1.endMark != time2.endMark:
            return False
        return True

    allTimes: {str: list[TimeRange]} = {
        'rTimes': rTimes,
        'exTimes': exTimes
    }

    for key, value in allTimes.items():
        # 遍历 rTimes 和 exTimes
        for time in value:
            # 如果曾创建过一样的时间片，恢复 deleted 为 false
            if any(equal(time, t) for t in times):
                for _t in times:
                    if equal(time, _t):
                        t = _t
                        break
                t.excluded = False if key == 'rTimes' else True
                t.deleted = False
                t.version += 1
                t.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
                t.save()
            # 如果没有创建过，创建新的时间片
            else:
                t = Time(id=uuid.uuid4().hex, schedule_id=schedule.id,
                         excluded=False if key == 'rTimes' else True,
                         start=time.start, end=time.end,
                         startMark=time.startMark, endMark=time.endMark, done=False,
                         created=isoformat(datetime.now().astimezone(tz.gettz('UTC'))),
                         updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
                t.save()

    # 不包括在 rTimes 和 exTimes 的内容要彻底删除，只标记 deleted 为 true 会导致 exTime 多出意外值
    toDel = difference(times, rTimes + exTimes, equal)

    # 需要删除的时间片
    for time in toDel:
        time.deleted = True
        time.version += 1
        time.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
        time.save()

    return schedule.to_dict()


def findEventsBetween(userId: str, start: str, end: str):
    times = (Time.objects.filter(
        schedule__user_id=userId,
        excluded=False,
        start__isnull=False,
        start__gte=isoformat(datetime.fromisoformat(start).astimezone(tz.gettz('UTC'))),
        end__lte=isoformat(datetime.fromisoformat(end).astimezone(tz.gettz('UTC'))),
        done=False,
        deleted=False)
             .order_by('start')
             .values('id', 'schedule_id',
                     'schedule__name', 'schedule__comment',
                     'start', 'end',
                     'startMark', 'endMark'))
    res: list[EventBriefVO] = []
    for time in times:
        res.append(EventBriefVO(id=time['id'], scheduleId=time['schedule_id'],
                                name=time['schedule__name'], comment=time['schedule__comment'],
                                start=time['start'], end=time['end'],
                                startMark=time['startMark'], endMark=time['endMark']).to_dict())
    return res


def findAllTodos(userId: str):
    firstTodos: list[TodoBriefVO] = []
    todayTodos: list[TodoBriefVO] = []
    todos = Schedule.objects.filter(user_id=userId, type=EventType.TODO, deleted=False).values('id', 'name')
    for todo in todos:
        time = (Time.objects.filter(
            schedule__id=todo['id'],
            excluded=False,
            # 每天的 start time 作为逻辑上的次日开始时间，未达次日 start time 就过期的 _todo 显示 expired，而不是直接消失
            end__gte=isoformat((datetime.now()
                                + relativedelta(
                        hour=getSettingByPath(userId, 'preferences.startTime.hour'),
                        minute=getSettingByPath(userId, 'preferences.startTime.minute')))
                               .astimezone(tz.gettz('UTC'))),
            deleted=False)
                .order_by('end')
                .values('id', 'end', 'done')).first()
        if time is not None:
            firstTodos.append(TodoBriefVO(id=time['id'], scheduleId=todo['id'],
                                          name=todo['name'], end=time['end'], done=time['done']))

    times = (Time.objects.filter(
        schedule__user_id=userId,
        schedule__type=EventType.TODO,
        schedule__deleted=False,
        excluded=False,
        # 每天的 start time 作为逻辑上的次日开始时间，未达次日 start time 就过期的 _todo 显示 expired，而不是直接消失
        end__gte=isoformat((datetime.now()
                            + relativedelta(
                    hour=getSettingByPath(userId, 'preferences.startTime.hour'),
                    minute=getSettingByPath(userId, 'preferences.startTime.minute')))
                           .astimezone(tz.gettz('UTC'))),
        end__lte=isoformat((datetime.now()
                            + relativedelta(days=1)
                            + relativedelta(
                    hour=getSettingByPath(userId, 'preferences.startTime.hour'),
                    minute=getSettingByPath(userId, 'preferences.startTime.minute')))
                           .astimezone(tz.gettz('UTC'))),
        deleted=False)
             .order_by('end')
             .values('id', 'schedule_id', 'end', 'done'))

    for time in times:
        todo = Schedule.objects.values('id', 'name').get(id=time['schedule_id'], user_id=userId)  # 上面已经保证 deleted 为 false
        todayTodos.append(
            TodoBriefVO(id=time['id'], scheduleId=time['schedule_id'],
                        name=todo['name'], end=time['end'], done=time['done']))

    res = union(firstTodos, todayTodos, lambda a, b: a.id == b.id)
    res = list(map(lambda todo: todo.to_dict(), res))

    return res


def findScheduleById(id: str, userId: str):
    schedule = Schedule.objects.get(id=id, user_id=userId)
    return schedule.to_dict()


def findTimesByScheduleId(scheduleId: str, userId: str):
    times = Time.objects.filter(schedule_id=scheduleId, schedule__user_id=userId, excluded=False, deleted=False)
    times = list(map(lambda time: time.to_dict(), times))
    return times


def findRecordsByScheduleId(scheduleId: str, userId: str):
    records = Record.objects.filter(schedule_id=scheduleId, schedule__user_id=userId, deleted=False)
    records = list(map(lambda record: record.to_dict(), records))
    return records


@transaction.atomic
def deleteScheduleById(id: str, userId: str):
    # 级联更新 deleted = true
    schedule = Schedule.objects.get(id=id, user_id=userId)
    schedule.deleted = True
    schedule.version += 1
    schedule.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    schedule.save()
    Time.objects.filter(schedule__id=id).update(deleted=True, version=F('version') + 1,
                                                updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
    Record.objects.filter(schedule__id=id).update(deleted=True, version=F('version') + 1,
                                                  updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
    return schedule.to_dict()


@transaction.atomic
def deleteTimeById(userId: str, id: str):
    time = Time.objects.get(schedule__user_id=userId, id=id).update(excluded=True)

    startTime: datetime
    endTime = datetime.fromisoformat(time.end).astimezone(tz.gettz('UTC'))
    endHour = endTime.hour if time.endMark[0] == '1' else '?'
    endMinute = endTime.minute if time.endMark[1] == '1' else '?'
    exTimeCode: str
    if time.start is not None:
        startTime = datetime.fromisoformat(time.start).astimezone(tz.gettz('UTC'))
        startHour = startTime.hour if time.startMark[0] == '1' else '?'
        startMinute = startTime.minute if time.startMark[1] == '1' else '?'
        exTimeCode = f'{startTime.strftime("%Y/%m/%d")} {startHour}:{startMinute}-{endHour}:{endMinute} UTC'
    else:
        exTimeCode = f'{endTime.strftime("%Y/%m/%d")} {endHour}:{endMinute} UTC'

    schedule = Schedule.objects.get(id=time.schedule.id, user_id=userId)

    schedule.exTimeCode = exTimeCode if schedule.exTimeCode == '' else f'{schedule.exTimeCode};{exTimeCode}'
    schedule.version += 1
    schedule.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    schedule.save()

    return time.to_dict()


def deleteTimeByIds(userId: str, ids: list[str]):
    for id in ids:
        deleteTimeById(userId, id)


def updateTimeCommentById(userId: str, id: str, comment: str):
    time = Time.objects.get(schedule__user_id=userId, id=id)
    time.comment = comment
    time.version += 1
    time.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    time.save()
    return time.to_dict()


class FindAllSchedulesConditions:
    search: str
    dateRange: list[int, int] | None
    type: str | None
    star: bool | None

    def __init__(self, conditions):
        self.search = conditions['search']
        if 'dateRange' in conditions:
            self.dateRange = conditions['dateRange']
        if 'type' in conditions:
            self.type = conditions['type']
        if 'star' in conditions:
            self.star = conditions['star']


def findAllSchedules(userId: str, conditions: FindAllSchedulesConditions, page: int, pageSize: int):
    schedules = Schedule.objects.filter(user_id=userId)
    schedules = (schedules.filter(name__icontains=conditions.search)
                 | schedules.filter(comment__icontains=conditions.search)
                 | schedules.filter(times__comment__icontains=conditions.search))
    if conditions.dateRange is not None:
        schedules = (schedules.filter(times__start__isnull=True,
                                      times__end__gte=isoformat(datetime.fromtimestamp(
                                          conditions.dateRange[0] / 1000).astimezone(tz.gettz('UTC'))),
                                      times__end__lte=isoformat(datetime.combine(
                                          datetime.fromtimestamp(conditions.dateRange[1] / 1000), datetime.max.time())
                                                                .astimezone(tz.gettz('UTC'))))
                     | schedules.filter(times__start__isnull=False,
                                        times__start__gte=isoformat(datetime.fromtimestamp(
                                            conditions.dateRange[0] / 1000).astimezone(tz.gettz('UTC'))),
                                        times__end__lte=isoformat(datetime.combine(
                                            datetime.fromtimestamp(conditions.dateRange[1] / 1000), datetime.max.time())
                                                                  .astimezone(tz.gettz('UTC')))))
        schedules = schedules.filter(times__deleted=False)
    schedules = schedules.distinct()
    if conditions.type is not None:
        schedules = schedules.filter(type=conditions.type)
    if conditions.star is not None:
        schedules = schedules.filter(star=conditions.star)
    schedules = schedules.order_by('created').values('id', 'type', 'name', 'star', 'deleted', 'created', 'updated')

    count = schedules.count()

    paginator = Paginator(schedules, pageSize)
    schedules = paginator.get_page(page)

    res: list[ScheduleBriefVO] = []
    for schedule in schedules:
        res.append(ScheduleBriefVO(id=schedule['id'], type=schedule['type'], name=schedule['name'],
                                   star=schedule['star'], deleted=schedule['deleted'], created=schedule['created'],
                                   updated=schedule['updated']).to_dict())

    return {
        'data': res,
        'total': count
    }


def updateDoneById(userId: str, id: str, done: bool):
    time = Time.objects.get(schedule__user_id=userId, id=id)
    time.done = done
    time.version += 1
    time.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    time.save()
    return time.to_dict()


def updateStarById(userId: str, id: str, star: bool):
    schedule = Schedule.objects.get(user_id=userId, id=id)
    schedule.star = star
    schedule.version += 1
    schedule.updated = isoformat(datetime.now().astimezone(tz.gettz('UTC')))
    schedule.save()
    return schedule.to_dict()


def createRecord(scheduleId: str, userId: str, startTime: str, endTime: str):
    record = Record(id=uuid.uuid4().hex, schedule_id=scheduleId,
                    start=startTime, end=endTime,
                    created=isoformat(datetime.now().astimezone(tz.gettz('UTC'))),
                    updated=isoformat(datetime.now().astimezone(tz.gettz('UTC'))))
    record.save()
    return record.to_dict()


@transaction.atomic
def sync(userId: str, schedules: list[dict], times: list[dict], records: list[dict], syncAt: str):
    print(schedules, times, records, syncAt)
    updated = {
        'schedules': [],
        'times': [],
        'records': [],
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

    for schedule in schedules:
        scheduleServer = Schedule.objects.filter(id=schedule['id'], user_id=userId).first()
        if update(scheduleServer, schedule):
            schedule['user_id'] = userId
            schedule['syncAt'] = syncAt
            schedule['version'] += 1
            Schedule.objects.update_or_create(id=schedule['id'], user_id=userId, defaults=schedule)
            updated['schedules'].append(schedule['id'])

    for time in times:
        timeServer = Time.objects.filter(schedule__user_id=userId, id=time['id']).first()
        if update(timeServer, time):
            time['schedule_id'] = time.pop('scheduleId')
            time['syncAt'] = syncAt
            time['version'] += 1
            Time.objects.update_or_create(schedule__user_id=userId, id=time['id'], defaults=time)
            updated['times'].append(time['id'])

    for record in records:
        recordServer = Record.objects.filter(schedule__user_id=userId, id=record['id']).first()
        if update(recordServer, record):
            record['schedule_id'] = record.pop('scheduleId')
            record['syncAt'] = syncAt
            record['version'] += 1
            Record.objects.update_or_create(schedule__user_id=userId, id=record['id'], defaults=record)
            updated['records'].append(record['id'])

    return updated


def getUnSynced(userId: str, lastSyncAt: str):
    schedules = Schedule.objects.filter(user_id=userId, updated__gt=lastSyncAt)
    times = Time.objects.filter(schedule__user_id=userId, updated__gt=lastSyncAt)
    records = Record.objects.filter(schedule__user_id=userId, updated__gt=lastSyncAt)

    return {
        'schedules': list(map(lambda schedule: schedule.to_dict(), schedules)),
        'times': list(map(lambda time: time.to_dict(), times)),
        'records': list(map(lambda record: record.to_dict(), records)),
    }
