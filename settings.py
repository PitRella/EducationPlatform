from envparse import Env

env = Env()

DATABASE_URL = env.str("DATABASE_URL",
                       default="postgresql+asyncpg:///postgres:postgres@0.0.0.0:5432/education_db")