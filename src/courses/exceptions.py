from fastapi import HTTPException


class CourseNotFoundByIdException(HTTPException):
    """Course cannot be found by id."""

    def __init__(self) -> None:
        """Initialize the CourseNotFoundByIdException with status 404."""
        super().__init__(
            status_code=404,
            detail='Active course cannot be not found.',
        )


class ThisUserDoesntBoughtTheCourseException(HTTPException):
    """This user doesn't buy the course."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404, detail='Current user does not bought the course'
        )

class CourseWasNotBoughtException(HTTPException):
    """Course was not bought."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404, detail='Course was not bought.'
        )