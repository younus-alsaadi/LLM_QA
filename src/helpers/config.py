from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging

THIS_DIR = Path(__file__).resolve().parent          # …/src/helpers
ENV_PATH = THIS_DIR.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: str
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class Config:
        env_file = ENV_PATH

def get_settings() -> Settings:
    return Settings()