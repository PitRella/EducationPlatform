from fastapi import HTTPException


class LessonIsNotPublishedException(HTTPException):
    """Exception raised when a lesson is not published or does not exist.

    This exception is typically used when attempting to retrieve a lesson
    that either cannot be found in the database or is marked as unpublished.
    It returns a 404 HTTP response.
    """

    def __init__(self) -> None:
        """Initialize the exception with a 404 status code and detail."""
        super().__init__(
            status_code=404,
            detail='Current lesson is not exist or not published'
        )


class LessonNotFoundByIdException(HTTPException):
    """Exception raised when a lesson with the given ID cannot be found.

    This exception is typically used when an operation references a lesson
    that does not exist in the database. It returns a 404 HTTP response.
    """

    def __init__(self) -> None:
        """Initialize the exception with a 404 status code and detail."""
        super().__init__(
            status_code=404,
            detail='Lesson was not found'
        )
