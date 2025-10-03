from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL_ASYNCPG_DRIVER: str
    DATABASE_URL_PSYCOPG_DRIVER: str
    PSYCOPG_CONNECT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    BUCKET_NAME: str

    SECRET_KEY: str
    SALT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JTI_EXPIRY_SECOND: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str

    BROKER_URL: str
    BACKEND_URL: str

    EMBEDDING_MODEL: str

    DOMAIN_NAME: str
    VERSION: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

Config = Settings()

#Celery config
broker_url = Config.BROKER_URL
backend_url = Config.BACKEND_URL
broker_connection_retry_on_startup = True
