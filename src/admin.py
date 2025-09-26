import logging

from fastapi import FastAPI
from sqladmin import Admin

from src.courses.admin import CourseAdmin
from src.database import engine
from src.lessons.admin import LessonAdmin
from src.users.admin import UserAdmin, AuthorAdmin
from src.settings import Settings

settings = Settings.load()
logger = logging.getLogger(__name__)



def initialize_admin_panel(app: FastAPI) -> None:
    if settings.DEBUG:
        logger.info('Initializing admin panel.')
        admin = Admin(app=app, engine=engine)
        admin.add_view(UserAdmin)
        admin.add_view(AuthorAdmin)
        admin.add_view(CourseAdmin)
        admin.add_view(LessonAdmin)
    else:
        logger.info('Debug mode is off, skipping admin panel initialization.')
    return None