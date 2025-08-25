from fastapi import HTTPException


class LessonIsNotPublishedException(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Current lesson is not exist or not published'
        )

class LessonNotFoundByIdException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Lesson was not found'
        )