import logging

import sentry_sdk
from fastapi import APIRouter, FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from src.auth.router import auth_router
from src.courses.router import course_router
from src.logger import configure_logging
from src.settings import Settings
from src.users.router import user_router

logger = logging.getLogger(__name__)

settings = Settings.load()
configure_logging()

sentry_sdk.init(
    dsn=settings.logging_settings.SENTRY_URL,
    send_default_pii=True,
)
app = FastAPI(title='EducationPlatform')
app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', handle_metrics)
main_api_router = APIRouter(prefix='/api/v1')
main_api_router.include_router(user_router, prefix='/user', tags=['user'])
main_api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
main_api_router.include_router(course_router, prefix='/course', tags=['course'])
app.include_router(main_api_router)

logger.info('Application started')
