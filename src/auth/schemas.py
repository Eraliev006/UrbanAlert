from pydantic import EmailStr
from sqlmodel import SQLModel


class LoginUserRead(SQLModel):
    email: EmailStr
    password: str

class LoginUserOutput(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPairs(SQLModel):
    access_token: str
    refresh_token: str