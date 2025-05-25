from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Forecasting API"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "forecast_db"
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: str = "5432"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "supersecret"

    model_config = ConfigDict(env_file=".env")

settings = Settings()