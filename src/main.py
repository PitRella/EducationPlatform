import sentry_sdk
from fastapi import FastAPI, APIRouter
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware

from src.settings import SENTRY_URL
from src.users.router import user_router
from src.auth.router import auth_router

sentry_sdk.init(
    dsn=SENTRY_URL,
    send_default_pii=True,
)
app = FastAPI(title="EducationPlatform")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)
main_api_router = APIRouter(prefix="/api/v1")
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(main_api_router)
