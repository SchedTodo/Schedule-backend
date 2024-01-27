from django.utils.deprecation import MiddlewareMixin


class CustomCsrfMiddleware(MiddlewareMixin):
    CLIENT_HEADER = 'x_client'

    def process_request(self, request):
        if request.META.get(f'HTTP_{self.CLIENT_HEADER.upper()}') == 'pc':
            # 设置一个标记，表明 CSRF 检查应该被跳过
            setattr(request, '_dont_enforce_csrf_checks', True)
