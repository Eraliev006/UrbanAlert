from pydantic import EmailStr
from sqlmodel import SQLModel

class LoginUserOutput(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPairs(SQLModel):
    access_token: str
    refresh_token: str

class VerifyEmailSchema(SQLModel):
    email_user: EmailStr
    otp_code: str

class RefreshTokenRequest(SQLModel):
    refresh_token: str

class NewAccessToken(SQLModel):
    new_access_token: str