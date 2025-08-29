import logging

import sentry_sdk
from fastapi import APIRouter, FastAPI
from sqladmin import Admin
from starlette_exporter import PrometheusMiddleware, handle_metrics

from src.auth.router import auth_router
from src.courses.admin import CourseAdmin
from src.courses.router import course_router
from src.database import engine
from src.lessons.router import lesson_router
from src.logger import configure_logging
from src.payment.router import payment_router
from src.settings import Settings
from src.users.admin import AuthorAdmin, UserAdmin
from src.users.routers import author_router, user_router
from src.users.routers.admin import admin_router

logger = logging.getLogger(__name__)

settings = Settings.load()
configure_logging()

sentry_sdk.init(
    dsn=settings.logging_settings.SENTRY_URL,
    send_default_pii=True,
)
app = FastAPI(title='EducationPlatform')
admin = Admin(app, engine)

admin.add_view(UserAdmin)
admin.add_view(AuthorAdmin)
admin.add_view(CourseAdmin)

app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', handle_metrics)
main_api_router = APIRouter(prefix='/api/v1')
main_api_router.include_router(user_router, prefix='/user', tags=['user'])
main_api_router.include_router(admin_router, prefix='/admin', tags=['admin'])
main_api_router.include_router(author_router, prefix='/author', tags=['author'])
main_api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
main_api_router.include_router(course_router, prefix='/course', tags=['course'])
main_api_router.include_router(lesson_router, prefix='/lesson', tags=['lesson'])
main_api_router.include_router(payment_router, prefix='/payment', tags=['payment'])
app.include_router(main_api_router)

logger.info('Application started')
