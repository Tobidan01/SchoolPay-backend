from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    NOMBA_BASE_URL: str

    NOMBA_CLIENT_ID: str
    NOMBA_PRIVATE_KEY: str

    NOMBA_PARENT_ACCOUNT_ID: str
    NOMBA_SUB_ACCOUNT_ID: str

    NOMBA_WEBHOOK_SECRET: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()