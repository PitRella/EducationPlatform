from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class StripePaymentSettings(BaseSettings):
    """Payment-related settings."""

    model_config = SettingsConfigDict(
        env_prefix='STRIPE_', env_file=BASE_DIR / '.env', extra='ignore'
    )
    SECRET_KEY: str = ''


class TokenSettings(BaseSettings):
    """Token-related settings."""

    model_config = SettingsConfigDict(
        env_prefix='TOKEN_', env_file=BASE_DIR / '.env', extra='ignore'
    )

    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


class DatabaseSettings(BaseSettings):
    """Database-related settings."""

    model_config = SettingsConfigDict(
        env_prefix='DB_', env_file=BASE_DIR / '.env', extra='ignore'
    )

    DATABASE_URL: str = ''


class LoggingSettings(BaseSettings):
    """Logging-related settings."""

    model_config = SettingsConfigDict(
        env_prefix='LOGGING_', env_file=BASE_DIR / '.env', extra='ignore'
    )

    SENTRY_URL: str = ''


class Settings(BaseSettings):
    """Base settings class for the application."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    # Log level
    LOG_LEVEL: str = 'INFO'

    # Nested settings
    token_settings: TokenSettings = Field(
        default_factory=TokenSettings
    )
    stripe_settings: StripePaymentSettings = Field(
        default_factory=StripePaymentSettings
    )
    database_settings: DatabaseSettings = Field(
        default_factory=DatabaseSettings
    )
    logging_settings: LoggingSettings = Field(
        default_factory=LoggingSettings
    )

    @classmethod
    def load(cls) -> 'Settings':
        """Return a new instance of Settings."""
        return cls()
