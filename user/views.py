import asyncio
import json
import os
import secrets
import uuid

from django.db import transaction
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponse

from main.decorators import errorHandler, checkToken
from main.settings import BASE_DIR
from main.consumer import send_message_to_user, Apis
from utils.auth import getToken
from utils.env import getHost
from . import service
from .models import ScheduleUser


# Create your views here.
def googleLogin(request):
    uid = request.GET.get('uid')
    print('googleLogin', uid)
    # 创建 Flow 实例
    flow = Flow.from_client_secrets_file(
        os.path.join(BASE_DIR, 'user/client_secret.json'),
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=f'{getHost()}/user/googleCallback/',
    )

    # 构造认证 URL 并重定向
    authorization_url, state = flow.authorization_url()
    request.session['state'] = state
    request.session['uid'] = uid

    return redirect(authorization_url)


@transaction.atomic
def googleCallback(request):
    state = request.session['state']
    uid = request.session['uid']

    flow = Flow.from_client_secrets_file(
        os.path.join(BASE_DIR, 'user/client_secret.json'),
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'],
        state=state,
        redirect_uri=f'{getHost()}/user/googleCallback/'
    )

    # 使用返回的授权码获取令牌
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    if not flow.credentials:
        return HttpResponse(status=401)

    # 获取用户信息
    session = flow.authorized_session()
    profile_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()

    # 在这里你可以根据 profile_info 创建或更新你的用户
    user, created = ScheduleUser.objects.get_or_create(
        email=profile_info['email'],
        defaults={
            'id': uuid.uuid4().hex,
            'username': profile_info['email'],
            'first_name': profile_info['given_name'],
            'last_name': profile_info['family_name'],
            'profile_image_url': profile_info['picture'],
            'locale': profile_info['locale'],
        })
    print('user', user, created)
    token = secrets.token_hex(16)
    cache.set(token, user.id, 60 * 60 * 24 * 7)  # 保存 7 天

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            send_message_to_user(
                uid,
                Apis.LOGIN,
                {
                    'token': token,
                    'userId': user.id,
                }
            ))
    finally:
        loop.close()
        asyncio.set_event_loop(None)  # 重置事件循环

    return HttpResponse(status=200)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def logout(request, userId):
    token = getToken(request)
    cache.delete(token)


@errorHandler
@checkToken
@require_http_methods(["POST"])
def getProfile(request, userId):
    return service.getProfileById(userId)
