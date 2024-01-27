
def getToken(request):
    TOKEN_HEADER = 'x_auth_token'
    token = request.META.get(f'HTTP_{TOKEN_HEADER.upper()}')
    return token


def getUserId(request):
    USERID_HEADER = 'x_auth_user_id'
    userId = request.META.get(f'HTTP_{USERID_HEADER.upper()}')
    return userId
