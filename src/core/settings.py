from pathlib import Path

from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class JWT(BaseModel):
    secret_key: str
    access_expires_in_minutes: int
    refresh_expires_in_minutes: int
    algorithm: str

class SMTPSettings(BaseModel):
    user_email: EmailStr
    password: str
    hostname: str
    port: int

class Database(BaseModel):
    db_user: str
    db_name: str
    db_password: str
    db_host: str
    db_port: int

    def get_url(self) -> str:
            """
                :return: Return the string representing url to connect to database
            """
            return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

class RedisSettings(BaseModel):
    port: int
    host: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= BASE_DIR / '.env',
        env_nested_delimiter='__'
    )
    jwt: JWT
    database: Database
    smtp: SMTPSettings
    redis: RedisSettings
    server_host: str
    server_port: int


settings = Settings()