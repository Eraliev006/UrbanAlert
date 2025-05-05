from src.common import AuthException


class PasswordIsIncorrect(AuthException):
    def __init__(self):
        super().__init__(detail='Password is incorrect')


