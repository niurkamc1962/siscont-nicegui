# config.py
# Utilizando pydantic_settings.BaseSettings para cargar .env una sola vez

from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    API_BASE_URL: str
    SQL_USER: str
    SQL_PORT: int
    PORT: int = 9802
    STORAGE_SECRET: str
    JSON_OUTPUT_DIR: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()


# Funcion para crear el directorio de los archivos JSON
def get_output_dir():
    # Intenta obtener desde la variable de entorno
    output_dir = os.getenv("JSON_OUTPUT_DIR")

    if output_dir:
        return output_dir

    # Si no está definida, se usa la ruta por defecto relativa al archivo actual
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_dir = os.path.join(base_dir, "archivos_json")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir
