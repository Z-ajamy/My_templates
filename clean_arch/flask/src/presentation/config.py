from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="production")
    flask_debug: bool = Field(default=False)
    database_url: str = Field(...)


settings = AppSettings()
