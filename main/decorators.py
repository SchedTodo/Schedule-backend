from django.http import JsonResponse
from functools import wraps


TOKEN_HEADER = 'x_auth_token'


def checkToken(viewFunc):
    @wraps(viewFunc)
    def _wrappedView(request, *args, **kwargs):
        token = request.META.get(f'HTTP_{TOKEN_HEADER.upper()}')
        if not token:
            return JsonResponse({'error': 'No token provided'}, status=401)

        return viewFunc(request, *args, **kwargs)

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
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return _wrappedView
