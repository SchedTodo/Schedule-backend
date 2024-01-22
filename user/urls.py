from django.urls import path
from . import views

# 必须加上，且同 project 下 urls 中的 namespace 同值
app_name = 'user'

urlpatterns = [
    path('googleLogin/', views.googleLogin, name="googleLogin"),
    path('googleCallback/', views.googleCallback, name="googleCallback"),
    path('getProfile/', views.getProfile, name='getProfile'),
]