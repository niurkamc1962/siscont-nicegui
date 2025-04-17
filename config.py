# config.py
# Utilizando pydantic_settings.BaseSettings para cargar .env una sola vez

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SQL_USER: str
    SQL_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
