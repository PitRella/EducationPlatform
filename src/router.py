from fastapi import APIRouter

from src.auth.router import auth_router
from src.courses.router import course_router
from src.lessons.router import lesson_router
from src.payment.routers import payment_router, webhooks_payment_router
from src.settings import Settings
from src.users.routers import author_router, user_router
from src.users.routers.admin import admin_router

settings = Settings.load()


def initialize_routers() -> APIRouter:
    """Initialize routers for the application."""
    main_api_router = APIRouter(prefix=f'/api/{settings.API_VERSION}')
    main_api_router.include_router(user_router, prefix='/user', tags=['user'])
    main_api_router.include_router(
        admin_router, prefix='/admin', tags=['admin']
    )
    main_api_router.include_router(
        author_router, prefix='/author', tags=['author']
    )
    main_api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
    main_api_router.include_router(
        course_router, prefix='/course', tags=['course']
    )
    main_api_router.include_router(
        lesson_router, prefix='/lesson', tags=['lesson']
    )
    main_api_router.include_router(
        payment_router, prefix='/payment', tags=['payment']
    )
    main_api_router.include_router(
        webhooks_payment_router, prefix='/payment/webhooks', tags=['payment']
    )

    return main_api_router
