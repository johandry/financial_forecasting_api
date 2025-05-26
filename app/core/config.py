import os
import logging

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env = os.getenv("ENV", "")
if env:
    env = f".{env}"
env_file = os.getenv("ENV_FILE", f".env{env}")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Forecasting API"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "forecast_db"
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: str = "5432"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "$uper$ecre7!"
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file=env_file)


settings = Settings()
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logging.debug(f"Using environment file: {env_file}")
logging.debug(f"PostgreSQL Server: {settings.POSTGRES_SERVER}")
logging.debug(f"Redis URL: {settings.REDIS_URL}")
