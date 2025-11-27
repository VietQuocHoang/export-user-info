from functools import lru_cache

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Export User Info"
    app_host: str = "localhost"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    limit: int = 10
    window_time: int = 10
    db_host: str = "localhost"
    db_user: str = "root"
    db_password: str = "123"
    db_name: str = "user_management"
    db_port: int = 5432
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
