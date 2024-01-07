from django.urls import path
from . import views

# 必须加上，且同 project 下 urls 中的 namespace 同值
app_name = 'schedule'

urlpatterns = [
    path('hello/', views.hello, name="hello"),
]