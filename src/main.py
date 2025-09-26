import logging

import sentry_sdk
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from src.admin import initialize_admin_panel
from src.logger import configure_logging
from src.router import initialize_routers
from src.settings import Settings

logger = logging.getLogger(__name__)

settings = Settings.load()
configure_logging()

if not settings.DEBUG:  # In debug mode we don't want to initialize sentry
    sentry_sdk.init(
        dsn=settings.logging_settings.SENTRY_URL,
        send_default_pii=True,
    )
app = FastAPI(title=settings.API_TITLE)
initialize_admin_panel(app=app)  # Initialize an admin panel before routers
main_api_router = (
    initialize_routers()
)  # Initialize routers after admin panel initialization
app.include_router(main_api_router)
app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', handle_metrics)
logger.info('Application started')
