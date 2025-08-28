from fastapi import HTTPException


class CourseNotFoundByIdException(HTTPException):
    """Exception raised when a course cannot be found by its ID."""

    def __init__(self) -> None:
        """Initialize the exception with HTTP 404 status code."""
        super().__init__(
            status_code=404,
            detail='Active course cannot be not found.',
        )


class ThisUserDoesntBoughtTheCourseException(HTTPException):
    """Exception raised when a user has not purchased a course."""

    def __init__(self) -> None:
        """Initialize the exception with HTTP 404 status code."""
        super().__init__(
            status_code=404,
            detail='Current user does not bought the course',
        )


class CourseWasNotBoughtException(HTTPException):
    """Exception raised when a course purchase operation fails."""

    def __init__(self) -> None:
        """Initialize the exception with HTTP 404 status code."""
        super().__init__(
            status_code=404,
            detail='Course was not bought.',
        )
