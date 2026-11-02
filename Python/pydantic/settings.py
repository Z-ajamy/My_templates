from pydantic import Field, SecretStr, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache

class AppSettings(BaseSettings):
    """
    Core application settings template adhering to 12-Factor App principles.
    Validates environment variables at startup and coerces types automatically.
    """

    # --- 1. Pydantic Settings Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Case insensitive by default (e.g., matching 'database_url' or 'DATABASE_URL')
        case_sensitive=False,
        # Allow extra env vars to exist in the OS without causing validation errors
        extra="ignore",
        # Prefix filtering (optional): If set to "APP_", it only looks for vars starting with "APP_"
        env_prefix="",
    )

    # --- 2. Environment & Application State ---
    # Enforces strict categorical values for the environment
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = Field(
        default="development"
    )
    DEBUG: bool = Field(default=False)
    
    # --- 3. Server Configuration ---
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=5000, ge=1024, le=65535) # Validates port range

    # --- 4. Database Connections (Strict DSN Validation) ---
    # PostgresDsn validates scheme (postgresql:// or postgres://) and connection structure
    DATABASE_URL: PostgresDsn
    # RedisDsn validates redis:// or rediss:// schemas
    REDIS_URL: RedisDsn | None = Field(default=None)
    
    # Example of database pooling limits
    DB_POOL_SIZE: int = Field(default=5, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0)

    # --- 5. Security & Cryptography ---
    # SecretStr prevents accidental logging/printing of sensitive data. 
    # Must use .get_secret_value() to read the actual string in code.
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)

    # --- 6. External Services / APIs ---
    # AnyHttpUrl ensures valid HTTP/HTTPS formatting
    EXTERNAL_API_BASE_URL: str | None = Field(default=None)
    API_TIMEOUT_SECONDS: float = Field(default=5.0)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

# --- 7. Instantiation with Singleton Pattern via lru_cache ---
@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Returns a cached instance of AppSettings.
    Prevents reading the .env file and OS environment multiple times.
    """
    return AppSettings()

# Usage Example:
# settings = get_settings()
# db_url = str(settings.DATABASE_URL)
# jwt_key = settings.SECRET_KEY.get_secret_value()
