import datetime as dt
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import PermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.courses.dependencies import (
    CoursePermissionDependency,
)
from src.courses.models import Course
from src.courses.permissions import (
    IsCourseActive,
    IsAuthorCourse
)
from src.courses.schemas import (
    BaseCourseResponseSchema,
    BaseCreateCourseRequestSchema,
    UpdateCourseRequestSchema,
)
from src.courses.service import CourseService
from src.users import User
from src.users.dependencies.author import AuthorPermissionDependency
from src.users.models import Author
from src.users.permissions import IsAuthorPermission

course_router = APIRouter()


@course_router.get('/all', response_model=list[BaseCourseResponseSchema])
async def get_all_courses(
        service: Annotated[CourseService, Depends(get_service(CourseService))],
        created_at: dt.datetime | None = None,
        last_id: uuid.UUID | None = None,
        limit: int | None = None,
) -> list[BaseCourseResponseSchema] | None:
    """Retrieve a list of all available courses with optional filtering.

    Args:
        service (CourseService): Service for course operations.
        created_at (datetime, optional): Filter created courses by timestamp.
        last_id (UUID, optional): Get courses after this course ID.
        limit (int, optional): Maximum number of courses to return.

    Returns:
        list[BaseCourseResponseSchema]: List of course objects.
        None if no courses are found.

    """
    courses: list[Course] = await service.get_all_courses(
        created_at, last_id, limit
    )
    return [BaseCourseResponseSchema.model_validate(c) for c in courses]


@course_router.post('/', response_model=BaseCourseResponseSchema)
async def create_course(
        course_schema: BaseCreateCourseRequestSchema,
        author: Annotated[
            Author, Security(
                AuthorPermissionDependency([IsAuthorPermission]))],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Create a new course.

    Args:
        course_schema (BaseCreateCourseRequestSchema): Schema containing course details.
        author (Author): The authenticated author creating the course.
        service (CourseService): Service for course operations.

    Returns:
        BaseCourseResponseSchema: The created course data.

    """
    course = await service.create_course(
        author=author, course_schema=course_schema
    )
    return BaseCourseResponseSchema.model_validate(course)


@course_router.get('/{course_id}', response_model=BaseCourseResponseSchema)
async def get_course(
        course: Annotated[
            Course,
            Security(
                CoursePermissionDependency(
                    [
                        IsCourseActive,
                        IsAuthorCourse
                    ]
                )
            )
        ],
) -> BaseCourseResponseSchema:
    """Retrieve a specific course by its ID.

    Args:
        course (Course): The course object retrieved by ID dependency.

    Returns:
        BaseCourseResponseSchema: The course data.

    """
    return BaseCourseResponseSchema.model_validate(course)


@course_router.patch('/{course_id}', response_model=BaseCourseResponseSchema)
async def update_course(
        course_id: uuid.UUID,
        course_fields: UpdateCourseRequestSchema,
        author: Annotated[
            Author, Security(
                AuthorPermissionDependency([IsAuthorPermission]))],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Update an existing course by its ID.

    Args:
        course_id (uuid.UUID): The unique identifier of the course to update.
        course_fields (UpdateCourseRequestSchema): Fields to update.
        author (Author): The authenticated author performing the update.
        service (CourseService): Service for course operations.

    Returns:
        BaseCourseResponseSchema: The updated course data.

    """
    updated_course = await service.update_course(
        course_id=course_id, author=author, course_fields=course_fields
    )
    return BaseCourseResponseSchema.model_validate(updated_course)


@course_router.delete('/{course_id}', status_code=204)
async def deactivate_course_by_id(
        course_id: uuid.UUID,
        author: Annotated[
            Author, Security(
                AuthorPermissionDependency([IsAuthorPermission]))],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> None:
    """Deactivate a course by its ID.

    Args:
        course_id (uuid.UUID): The unique id of the course to deactivate.
        author (Author): The authenticated author performing the deactivation.
        service (CourseService): Service for course operations.

    Returns:
        None

    Note:
        This endpoint returns a 204 status code on successful deactivation.

    """
    await service.deactivate_course(course_id=course_id, author=author)


@course_router.post('/purchase/{course_id}', status_code=201)
async def purchase_course_by_id(
        user: Annotated[
            User, Security(PermissionDependency([IsAuthenticated]))],
        course: Annotated[
            Course,
            Security(
                CoursePermissionDependency(
                    [
                        IsCourseActive,
                        IsAuthorCourse
                    ]
                )
            )
        ],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> None:
    pass
