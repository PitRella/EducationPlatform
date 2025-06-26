from envparse import Env  # type: ignore

env = Env()

# Settings for JWT
SECRET_KEY: str = env.str("SECRET_KEY", default="my-secret-key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")

# Token expire time
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int(
    "ACCESS_TOKEN_EXPIRE_MINUTES", default=15
)
REFRESH_TOKEN_EXPIRE_DAYS: int = env.int(
    "REFRESH_TOKEN_EXPIRE_DAYS", default=30
)

# Database settings
DATABASE_URL: str = env.str(
    "DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/education_db",
)

# Sentry url
SENTRY_URL: str = env.str("SENTRY_URL", default="")

# Logger
LOG_LEVEL: str = env.str("LOG_LEVEL", default="INFO")
