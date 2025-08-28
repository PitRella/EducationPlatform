import datetime as dt
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import UserPermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.courses.dependencies import (
    CoursePermissionDependency,
)
from src.courses.models import Course
from src.courses.permissions import IsAuthorCourse, IsCourseActive
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
        created_at (datetime, optional): Filter courses created after this
            timestamp.
        last_id (UUID, optional): Get courses after this course ID.
        limit (int, optional): Maximum number of courses to return.

    Returns:
        list[BaseCourseResponseSchema] | None: List of course schemas or None
            if no courses exist.

    """
    courses: list[Course] = await service.get_all_courses(
        created_at, last_id, limit
    )
    return [BaseCourseResponseSchema.model_validate(c) for c in courses]


@course_router.post('/', response_model=BaseCourseResponseSchema)
async def create_course(
    course_schema: BaseCreateCourseRequestSchema,
    author: Annotated[
        Author, Security(AuthorPermissionDependency([IsAuthorPermission]))
    ],
    service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Create a new course.

    Only authenticated authors can create a course.

    Args:
        course_schema (BaseCreateCourseRequestSchema): Schema with course data.
        author (Author): Authenticated author creating the course.
        service (CourseService): Service for course operations.

    Returns:
        BaseCourseResponseSchema: The created course schema.

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
                [IsCourseActive, IsAuthorCourse], logic='OR'
            )
        ),
    ],
) -> BaseCourseResponseSchema:
    """Retrieve a specific course by its ID.

    A course can be retrieved if it is active or if the requester is the author.

    Args:
        course (Course): Course instance retrieved via permission dependency.

    Returns:
        BaseCourseResponseSchema: Schema of the course.

    """
    return BaseCourseResponseSchema.model_validate(course)


@course_router.patch('/{course_id}', response_model=BaseCourseResponseSchema)
async def update_course(
    course: Annotated[
        Course,
        Security(
            CoursePermissionDependency(
                [IsAuthorCourse],
            )
        ),
    ],
    service: Annotated[CourseService, Depends(get_service(CourseService))],
    course_fields: UpdateCourseRequestSchema,
) -> BaseCourseResponseSchema:
    """Update an existing course.

    Only the course author can update it. Changes are saved and returned.

    Args:
        course (Course): Course instance retrieved via permission dependency.
        service (CourseService): Service for course operations.
        course_fields (UpdateCourseRequestSchema): Schema with updated fields.

    Returns:
        BaseCourseResponseSchema: Schema of the updated course.

    """
    updated_course = await service.update_course(
        course=course, course_fields=course_fields
    )
    return BaseCourseResponseSchema.model_validate(updated_course)


@course_router.delete('/{course_id}', status_code=204)
async def deactivate_course_by_id(
    course: Annotated[
        Course,
        Security(
            CoursePermissionDependency(
                [IsAuthorCourse],
            )
        ),
    ],
    service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> None:
    """Deactivate a course by its ID.

    Only the course author can deactivate it. Deactivation marks the course
    as inactive.

    Args:
        course (Course): Course instance retrieved via permission dependency.
        service (CourseService): Service for course operations.

    Returns:
        None

    """
    await service.deactivate_course(course=course)


@course_router.post('/purchase/{course_id}', status_code=201)
async def purchase_course_by_id(
    user: Annotated[
        User, Security(UserPermissionDependency([IsAuthenticated]))
    ],
    course: Annotated[
        Course,
        Security(
            CoursePermissionDependency(
                [
                    IsCourseActive,
                ]
            )
        ),
    ],
    service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> None:
    """Purchase a course by its ID.

    The user must be authenticated. The course must be active.

    Args:
        user (User): Authenticated user purchasing the course.
        course (Course): Course instance retrieved via permission dependency.
        service (CourseService): Service for course operations.

    Returns:
        None

    """
    await service.purchase_course(course=course, user=user)
