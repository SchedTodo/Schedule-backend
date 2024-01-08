import uuid
from copy import deepcopy
from datetime import datetime
from django.core.paginator import Paginator

from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.db import transaction

from schedule.models import Schedule, Time, Record
from schedule.timeCodeParser import parseTimeCodes
from schedule.timeCodeParserTypes import TimeRange, EventType
from schedule.userSettings import getSettingsByPath
from utils.utils import difference, union
from utils.vo import EventBriefVO, TodoBriefVO, ScheduleBriefVO


@transaction.atomic
def createSchedule(name: str, timeCodes: str, comment: str, exTimeCodes: str):
    parseRes = parseTimeCodes(timeCodes, exTimeCodes)
    eventType, rTimes, exTimes, rruleStr, code, exCode = parseRes.eventType, parseRes.rTimes, parseRes.exTimes, parseRes.rruleStr, parseRes.rTimeCodes, parseRes.exTimeCodes

    schedule = Schedule(id=uuid.uuid4().hex, type=eventType, name=name, rrules=rruleStr, rTimeCode=code,
                        exTimeCode=exCode, comment=comment)
    schedule.save()

    for time in rTimes:
        time = Time(id=uuid.uuid4().hex, schedule_id=schedule.id, start=time.start, end=time.end, startMark=time.startMark,
                    endMark=time.endMark, done=False, deleted=False)
        time.save()

    for time in exTimes:
        time = Time(id=uuid.uuid4().hex, schedule_id=schedule.id, start=time.start, end=time.end, startMark=time.startMark,
                    endMark=time.endMark, done=False, deleted=True)
        time.save()

    return schedule.to_dict()


@transaction.atomic
def updateScheduleById(id: str, name: str, timeCodes: str, comment: str, exTimeCodes: str):
    oldSchedule = Schedule.objects.get(id=id)

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
    schedule.save()

    # 如果时间片没有变化，直接返回
    if oldSchedule.rTimeCode == code and oldSchedule.exTimeCode == exCode:
        return oldSchedule.to_dict()

    # 获取所有和该 Schedule 相关的时间片
    times = Time.objects.filter(schedule__id=id)

    def equal(time1: TimeRange | Time, time3: TimeRange | Time):
        """
        两个时间片相等的条件
        """
        if time1.start is not None and time1.end is not None:
            if datetime.fromisoformat(time1.start) != datetime.fromisoformat(time3.start):
                return False
        if datetime.fromisoformat(time1.end) != datetime.fromisoformat(time3.end):
            return False
        if time1.startMark != time3.startMark:
            return False
        if time1.endMark != time3.endMark:
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
                if key == 'rTimes':
                    t.deleted = False
                else:
                    t.deleted = True
                t.save()
            # 如果没有创建过，创建新的时间片
            else:
                t = Time(id=uuid.uuid4().hex, schedule_id=schedule.id, start=time.start, end=time.end,
                         startMark=time.startMark, endMark=time.endMark, done=False, deleted=key == 'exTimes')
                t.save()

    # 不包括在 rTimes 和 exTimes 的内容要彻底删除，只标记 deleted 为 true 会导致 exTime 多出意外值
    toDel = difference(times, rTimes + exTimes, equal)

    # 需要删除的时间片
    for time in toDel:
        time.deleted = True
        time.save()

    return schedule.to_dict()


def findEventsBetween(start: str, end: str):
    times = (Time.objects.filter(
        start__isnull=False,
        start__gte=datetime.fromisoformat(start).astimezone(tz.gettz('UTC')).isoformat(),
        end__lte=datetime.fromisoformat(end).astimezone(tz.gettz('UTC')).isoformat(),
        done=False,
        deleted=False)
             .order_by('start'))
    res: list[EventBriefVO] = []
    for time in times:
        event = Schedule.objects.get(type=EventType.EVENT, id=time.schedule.id, deleted=False)
        res.append(EventBriefVO(id=time.id, scheduleId=time.schedule.id, name=event.name, comment=event.comment,
                                start=time.start, end=time.end, startMark=time.startMark, endMark=time.endMark).to_dict())
    return res


def findAllTodos():
    firstTodos: list[TodoBriefVO] = []
    todayTodos: list[TodoBriefVO] = []
    todos = Schedule.objects.filter(type=EventType.TODO, deleted=False)
    for todo in todos:
        time = (Time.objects.filter(
            schedule__id=todo.id,
            # 每天的 start time 作为逻辑上的次日开始时间，未达次日 start time 就过期的 todo 显示 expired，而不是直接消失
            end__gte=(datetime.now()
                      + relativedelta(
                        hour=getSettingsByPath('preferences.startTime.hour'),
                        minute=getSettingsByPath('preferences.startTime.minute')))
            .astimezone(tz.gettz('UTC')).isoformat(),
            deleted=False)
                .order_by('end').first())
        if time is not None:
            firstTodos.append(TodoBriefVO(id=time.id, scheduleId=todo.id, name=todo.name, end=time.end, done=time.done))

    times = (Time.objects.filter(
        schedule__type=EventType.TODO,
        schedule__deleted=False,
        # 每天的 start time 作为逻辑上的次日开始时间，未达次日 start time 就过期的 todo 显示 expired，而不是直接消失
        end__gte=(datetime.now()
                  + relativedelta(
                    hour=getSettingsByPath('preferences.startTime.hour'),
                    minute=getSettingsByPath('preferences.startTime.minute')))
        .astimezone(tz.gettz('UTC')).isoformat(),
        end__lte=(datetime.now()
                  + relativedelta(days=1)
                  + relativedelta(
                    hour=getSettingsByPath('preferences.startTime.hour'),
                    minute=getSettingsByPath('preferences.startTime.minute'))),
        deleted=False)
             .order_by('end'))

    for time in times:
        todo = Schedule.objects.get(id=time.schedule.id)  # 上面已经保证 deleted 为 false
        todayTodos.append(
            TodoBriefVO(id=time.id, scheduleId=time.schedule.id, name=todo.name, end=time.end, done=time.done))

    res = union(firstTodos, todayTodos, lambda a, b: a.id == b.id)
    res = list(map(lambda todo: todo.to_dict(), res))

    return res


def findScheduleById(id: str):
    schedule = Schedule.objects.get(id=id)
    return schedule.to_dict()


def findTimesByScheduleId(scheduleId: str):
    times = Time.objects.filter(schedule_id=scheduleId, deleted=False)
    times = list(map(lambda time: time.to_dict(), times))
    return times


def findRecordsByScheduleId(scheduleId: str):
    records = Record.objects.filter(schedule_id=scheduleId, deleted=False)
    records = list(map(lambda record: record.to_dict(), records))
    return records


@transaction.atomic
def deleteScheduleById(id: str):
    # 级联更新 deleted = true
    schedule = Schedule.objects.get(id=id)
    schedule.deleted = True
    schedule.save()
    Time.objects.filter(schedule__id=id).update(deleted=True)
    Record.objects.filter(schedule__id=id).update(deleted=True)
    return schedule.to_dict()


@transaction.atomic
def deleteTimeById(id: str):
    time = Time.objects.get(id=id)
    time.deleted = True
    time.save()

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

    schedule = Schedule.objects.get(id=time.schedule.id)

    schedule.exTimeCode = exTimeCode if schedule.exTimeCode == '' else f'{schedule.exTimeCode};{exTimeCode}'
    schedule.save()

    return time.to_dict()


def deleteTimeByIds(ids: list[str]):
    for id in ids:
        deleteTimeById(id)


def updateTimeCommentById(id: str, comment: str):
    time = Time.objects.get(id=id)
    time.comment = comment
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


def findAllSchedules(conditions: FindAllSchedulesConditions, page: int, pageSize: int):
    schedules = (Schedule.objects.filter(name__icontains=conditions.search)
                 | Schedule.objects.filter(comment__icontains=conditions.search)
                 | Schedule.objects.filter(times__comment__icontains=conditions.search))
    if conditions.dateRange is not None:
        schedules = (schedules.filter(times__start__isnull=True,
                                      times__end__gte=datetime.fromtimestamp(conditions.dateRange[0] / 1000).astimezone(
                                          tz.gettz('UTC')).isoformat(),
                                      times__end__lte=datetime.combine(datetime.fromtimestamp(conditions.dateRange[1] / 1000), datetime.max.time())
                                      .astimezone(tz.gettz('UTC')).isoformat())
                     | schedules.filter(times__start__isnull=False,
                                        times__start__gte=datetime.fromtimestamp(
                                            conditions.dateRange[0] / 1000).astimezone(
                                            tz.gettz('UTC')).isoformat(),
                                        times__end__lte=datetime.combine(datetime.fromtimestamp(conditions.dateRange[1] / 1000), datetime.max.time())
                                        .astimezone(tz.gettz('UTC')).isoformat()))
        schedules = schedules.filter(times__deleted=False)
    schedules = schedules.distinct()
    if conditions.type is not None:
        schedules = schedules.filter(type=conditions.type)
    if conditions.star is not None:
        schedules = schedules.filter(star=conditions.star)
    schedules = schedules.order_by('created')

    count = schedules.count()

    paginator = Paginator(schedules, pageSize)
    schedules = paginator.get_page(page)

    res: list[ScheduleBriefVO] = []
    for schedule in schedules:
        res.append(ScheduleBriefVO(id=schedule.id, type=schedule.type, name=schedule.name,
                                   star=schedule.star, deleted=schedule.deleted, created=schedule.created,
                                   updated=schedule.updated).to_dict())

    return {
        'data': res,
        'total': count
    }


def updateDoneById(id: str, done: bool):
    time = Time.objects.get(id=id)
    time.done = done
    time.save()
    return time.to_dict()


def updateStarById(id: str, star: bool):
    schedule = Schedule.objects.get(id=id)
    schedule.star = star
    schedule.save()
    return schedule.to_dict()


def createRecord(scheduleId: str, startTime: str, endTime: str):
    print(startTime, endTime)
    record = Record(id=uuid.uuid4().hex, schedule_id=scheduleId, start=startTime, end=endTime)
    record.save()
    return record.to_dict()
