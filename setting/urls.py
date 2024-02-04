from django.urls import path
from . import views

# 必须加上，且同 project 下 urls 中的 namespace 同值
app_name = 'setting'

urlpatterns = [
    path('getSettings/', views.getSettings, name="getSettings"),
    path('setSettings/', views.setSettings, name="setSettings"),
    path('getSettingByPath/', views.getSettingByPath, name="getSettingByPath"),
    # path('setSettingByPath/', views.setSettingByPath, name="setSettingByPath"),
    path('sync/', views.sync, name="sync"),
    path('getUnSynced/', views.getUnSynced, name="getUnSynced"),
]
