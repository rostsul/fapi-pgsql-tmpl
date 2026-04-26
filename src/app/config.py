from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8000
    WORKERS: int = 2

    DATABASE_URL: str
    REDIS_URL: str

    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    SECRET_KEY: str = Field(min_length=32)

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
