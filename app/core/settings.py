from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


class Settings(BaseSettings):
    APP_NAME: str = "Janata REST API"
    TIMEZONE: str = "Asia/Kolkata"
    SECRET_KEY: str
    MONGO_URL: str
    DB_NAME: str
    ACCESS_TOKEN_EXPIRE_TIMEDELTA: int
    REFRESH_TOKEN_EXPIRE_TIMEDELTA: int
    ALGO: str

    ADMIN_NAME: str
    ADMIN_EMAIL: EmailStr
    ADMIN_PHONE: str
    ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
