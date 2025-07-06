from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Base settings class for the application."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    # Log level
    LOG_LEVEL: str = 'INFO'

    # Token settings
    TOKEN_SECRET_KEY: str = ''
    TOKEN_ALGORITHM: str = 'HS256'  # noqa: S105
    TOKEN_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    TOKEN_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database settings
    DB_DATABASE_URL: str = ''

    # Logging settings
    LOGGING_SENTRY_URL: str = ''

    @classmethod
    def load(cls) -> 'Settings':
        """Return a new instance of Settings."""
        return cls()
