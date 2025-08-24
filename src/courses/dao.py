from src.base.dao import BaseDAO
from src.courses.models import Course
from src.courses.schemas import BaseCreateCourseRequestSchema


class CourseDAO(BaseDAO[Course, BaseCreateCourseRequestSchema]):
    pass
