from django.urls import path
from . import views

# 必须加上，且同 project 下 urls 中的 namespace 同值
app_name = 'schedule'

urlpatterns = [
    path('createSchedule/', views.createSchedule, name="createSchedule"),
    path('updateScheduleById/', views.updateScheduleById, name="updateScheduleById"),
    path('findEventsBetween/', views.findEventsBetween, name="findEventsBetween"),
    path('findAllTodos/', views.findAllTodos, name="findAllTodos"),
    path('findScheduleById/', views.findScheduleById, name="findScheduleById"),
    path('findTimesByScheduleId/', views.findTimesByScheduleId, name="findTimesByScheduleId"),
    path('findRecordsByScheduleId/', views.findRecordsByScheduleId, name="findRecordsByScheduleId"),
    path('deleteScheduleById/', views.deleteScheduleById, name="deleteScheduleById"),
    path('deleteTimeByIds/', views.deleteTimeByIds, name="deleteTimeByIds"),
    path('updateTimeCommentById/', views.updateTimeCommentById, name="updateTimeCommentById"),
    path('findAllSchedules/', views.findAllSchedules, name="findAllSchedules"),
    path('updateDoneById/', views.updateDoneById, name='updateDoneById'),
    path('updateStarById/', views.updateStarById, name='updateStarById'),
    path('createRecord/', views.createRecord, name='createRecord'),
    path('sync/', views.sync, name='sync'),
    path('getUnSynced/', views.getUnSynced, name='getUnSynced'),
]
