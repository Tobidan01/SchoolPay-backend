from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str

    # ==========================
    # JWT
    # ==========================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================
    # Nomba
    # ==========================
    NOMBA_BASE_URL: str

    NOMBA_CLIENT_ID: str
    NOMBA_PRIVATE_KEY: str

    NOMBA_PARENT_ACCOUNT_ID: str
    NOMBA_SUB_ACCOUNT_ID: str

    # Make optional until you receive it
    NOMBA_WEBHOOK_SECRET: str

    # ==========================
    # App
    # ==========================
    APP_NAME: str = "SchoolPay API"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # ==========================
    # Frontend
    # ==========================
    FRONTEND_URL: str = "https://github.com/littlebigFM/SchoolPay"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()