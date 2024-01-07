import uuid
from datetime import datetime
from django.core.paginator import Paginator

from dateutil import tz
from dateutil.relativedelta import relativedelta

from schedule.models import Schedule, Time, Record
from schedule.timeCodeParser import parseTimeCodes
from schedule.timeCodeParserTypes import TimeRange, EventType
from schedule.userSettings import getSettingsByPath
from utils.utils import difference, union
from utils.vo import EventBriefVO, TodoBriefVO, ScheduleBriefVO


def createSchedule(name: str, timeCodes: str, comment: str, exTimeCodes: str):
    parseRes = parseTimeCodes(timeCodes, exTimeCodes)
    eventType, rTimes, exTimes, rruleStr, code, exCode = parseRes.eventType, parseRes.rTimes, parseRes.exTimes, parseRes.rruleStr, parseRes.rTimeCodes, parseRes.exTimeCodes

    schedule = Schedule(id=uuid.uuid4().hex, type=eventType, name=name, rrules=code, rTimeCode=rTimes,
                        exTimeCode=exTimes, comment=comment)
    schedule.save()

    for time in rTimes:
        time = Time(id=uuid.uuid4().hex, schedule_id=schedule, start=time.start, end=time.end, startMark=time.startMark,
                    endMark=time.endMark, done=False, deleted=False)
        time.save()

    for time in exTimes:
        time = Time(id=uuid.uuid4().hex, schedule_id=schedule, start=time.start, end=time.end, startMark=time.startMark,
                    endMark=time.endMark, done=False, deleted=True)
        time.save()

    return schedule


def updateScheduleById(id: str, name: str, timeCodes: str, comment: str, exTimeCodes: str):
    oldSchedule = Schedule.objects.get(id=id)

    if oldSchedule.deleted:
        raise Exception('try to update a deleted schedule')

    parseRes = parseTimeCodes(timeCodes, exTimeCodes)
    eventType, rTimes, exTimes, rruleStr, code, exCode = parseRes.eventType, parseRes.rTimes, parseRes.exTimes, parseRes.rruleStr, parseRes.rTimeCodes, parseRes.exTimeCodes

    if oldSchedule.type != eventType:
        raise Exception('try to change schedule type')

    schedule = Schedule(id=id, type=eventType, name=name, rrules=code, rTimeCode=rTimes,
                        exTimeCode=exTimes, comment=comment)
    schedule.save()

    # 如果时间片没有变化，直接返回
    if oldSchedule.rTimeCode == code and oldSchedule.exTimeCode == exCode:
        return oldSchedule

    # 获取所有和该 Schedule 相关的时间片
    times = Time.objects.filter(schedule_id=id)

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
                t = filter(lambda t: equal(time, t), list(times))
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

    return schedule


def findEventsBetween(start: str, end: str):
    times = (Time.objects.filter(
        start__is_null=False,
        times__start__lte=datetime.fromisoformat(start).astimezone(tz.gettz('UTC')).isoformat(),
        times__end__gte=datetime.fromisoformat(end).astimezone(tz.gettz('UTC')).isoformat(),
        done=False,
        deleted=False)
             .order_by('times__start'))
    res: list[EventBriefVO] = []
    for time in times:
        event = Schedule.objects.get(type=EventType.EVENT, id=time.schedule_id, deleted=False)
        # event 不是只有 1 个
        if event.size != 1:
            raise Exception(f'schedule {time.schedule_id} is not unique or not exist')
        res.append(EventBriefVO(id=time.id, scheduleId=time.schedule_id, name=event.name, comment=event.comment,
                                start=time.start, end=time.end, startMark=time.startMark, endMark=time.endMark))
    return res


def findAllTodos():
    firstTodos: list[TodoBriefVO] = []
    todayTodos: list[TodoBriefVO] = []
    todos = Schedule.objects.filter(type=EventType.TODO, deleted=False)
    for todo in todos:
        time = (Time.objects.filter(
            schedule_id=todo.id,
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
        todo = Schedule.objects.get(id=time.schedule_id)  # 上面已经保证 deleted 为 false
        todayTodos.append(
            TodoBriefVO(id=time.id, scheduleId=time.schedule_id, name=todo.name, end=time.end, done=time.done))

    res = union(firstTodos, todayTodos, lambda a, b: a.id == b.id)

    return res


def findScheduleById(id: str):
    schedule = Schedule.objects.get(id=id)
    return schedule


def findTimesByScheduleId(scheduleId: str):
    times = Time.objects.filter(schedule_id=scheduleId, deleted=False)
    return times


def findRecordsByScheduleId(scheduleId: str):
    records = Record.objects.filter(schedule_id=scheduleId, deleted=True)
    return records


def deleteScheduleById(id: str):
    # 级联更新 deleted = true
    Schedule.objects.filter(id=id).update(deleted=True)
    Time.objects.filter(schedule_id=id).update(deleted=True)
    Record.objects.filter(schedule_id=id).update(deleted=True)


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
        exTimeCode = f'{startTime.strftime("yyyy/MM/dd")} {startHour}:{startMinute}-{endHour}:{endMinute} UTC'
    else:
        exTimeCode = f'{endTime.strftime("yyyy/MM/dd")} {endHour}:{endMinute} UTC'

    schedule = Schedule.objects.get(id=time.schedule_id)

    if len(schedule) != 1:
        raise Exception(f'schedule {time.schedule_id} is not unique or not exist')

    schedule.exTimeCode = exTimeCode if schedule.exTimeCode == '' else f'{schedule.exTimeCode};{exTimeCode}'
    schedule.save()

    return time


def deleteTimeByIds(ids: list[str]):
    for id in ids:
        deleteTimeById(id)


def updateTimeCommentById(id: str, comment: str):
    time = Time.objects.get(id=id)
    time.comment = comment
    time.save()
    return time


class FindAllSchedulesConditions:
    search: str
    dateRange: list[int, int] | None
    type: str | None
    star: bool | None


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

    count = schedules.count()

    paginator = Paginator(schedules, pageSize)
    schedules = paginator.get_page(page)

    res: list[ScheduleBriefVO] = []
    for schedule in schedules:
        res.append(ScheduleBriefVO(id=schedule.id, type=schedule.type, name=schedule.name,
                                   star=schedule.star, deleted=schedule.deleted, created=schedule.created,
                                   updated=schedule.updated))

    return {
        'data': res,
        'total': count
    }


def updateDoneById(id: str, done: bool):
    time = Time.objects.get(id=id)
    time.done = done
    time.save()
    return time


def updateStarById(id: str, star: bool):
    schedule = Schedule.objects.get(id=id)
    schedule.star = star
    schedule.save()
    return schedule


def createRecord(scheduleId: str, startTime: str, endTime: str):
    record = Record(id=uuid.uuid4().hex, schedule_id=scheduleId, start=startTime, end=endTime)
    record.save()
    return record
