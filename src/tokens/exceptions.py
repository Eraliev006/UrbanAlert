from src.common import AuthException


class InvalidTokenType(AuthException):
    def __init__(self):
        super().__init__(detail='Token is of invalid type')


class RefreshTokenNotFound(AuthException):
    def __init__(self):
        super().__init__(detail='Refresh token not found')


class InvalidSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Invalid token signature error')


class ExpiredTokenSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Token expired')

class DecodeTokenError(AuthException):
    def __init__(self):
        super().__init__(
            detail='Error with decoding token'
        )