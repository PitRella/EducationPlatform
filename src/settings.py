from envparse import Env

env = Env()

# Settings for JWT
SECRET_KEY: str = env.str("SECRET_KEY", default="my-secret-key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES",
                                           default=30)
DATABASE_URL: str = env.str("DATABASE_URL",
                            default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/education_db")
