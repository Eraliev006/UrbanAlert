from sqlmodel import SQLModel


class TokenPairs(SQLModel):
    access_token: str
    refresh_token: str

class RefreshTokenRequest(SQLModel):
    refresh_token: str

class NewAccessToken(SQLModel):
    new_access_token: str