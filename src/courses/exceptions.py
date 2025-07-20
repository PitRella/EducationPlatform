from fastapi import HTTPException


class CourseNotFoundByIdException(HTTPException):
    """Course cannot be found by id."""

    def __init__(self) -> None:
        """Initialize the CourseNotFoundByIdException with status 404."""
        super().__init__(
            status_code=404,
            detail='Active course cannot be not found.',
        )
