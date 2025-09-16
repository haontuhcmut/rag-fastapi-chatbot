from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    PSYCOPG_CONNECT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    EMBEDDING_MODEL: str

    DOMAIN_NAME: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

Config = Settings()
