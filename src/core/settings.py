from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class JWT(BaseModel):
    public_key: str
    private_key: str
    access_expires_in_minutes: int
    refresh_expires_in_minutes: int
    algorithm: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= BASE_DIR / '.env',
        env_nested_delimiter='__'
    )
    jwt: JWT
    server_host: str
    server_port: int


settings = Settings()