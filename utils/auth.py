
def getToken(request):
    TOKEN_HEADER = 'x_auth_token'
    token = request.META.get(f'HTTP_{TOKEN_HEADER.upper()}')
    return token
