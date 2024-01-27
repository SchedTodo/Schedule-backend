from django.http import JsonResponse
from functools import wraps
from django.core.cache import cache

from user.models import ScheduleUser
from utils.auth import getToken, getUserId


def checkToken(viewFunc):
    @wraps(viewFunc)
    def _wrappedView(request, *args, **kwargs):
        token = getToken(request)
        if not token:
            return JsonResponse({'error': 'No token provided'}, status=401)

        userId = getUserId(request)
        if not userId:
            return JsonResponse({'error': 'No token provided'}, status=401)

        if not cache.get(token) or cache.get(token) != userId:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return viewFunc(request, userId, *args, **kwargs)

    return _wrappedView


def errorHandler(viewFunc: callable):
    @wraps(viewFunc)
    def _wrappedView(request, *args, **kwargs):
        try:
            res = viewFunc(request)

            if isinstance(res, JsonResponse):
                return res

            return JsonResponse({'success': True, 'data': res}, status=200)
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=200)
        except ScheduleUser.DoesNotExist as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return _wrappedView
