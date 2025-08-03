import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING
from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.exceptions import ThisUserDoesntBoughtTheCourseException
from src.users.models import UserCourses

if TYPE_CHECKING:
    from src.courses.models import Course
    from src.users.models import User

type UserCoursesDAO = BaseDAO[UserCourses]


class UserCoursesService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            dao: UserCoursesDAO | None = None,
    ) -> None:
        super().__init__(db_session)
        self._dao: UserCoursesDAO = dao or BaseDAO[
            UserCourses,
        ](session=db_session, model=UserCourses)

    async def user_bought_course(
            self,
            user: User,
            course_id: uuid.UUID,
    ) -> UserCourses:
        async with self.session.begin():
            user_course: UserCourses | None = await self._dao.get_one(
                user_id=user.id,
                course_id=course_id
            )
        if not user_course:
            raise ThisUserDoesntBoughtTheCourseException
        return user_course
