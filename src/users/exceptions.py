from fastapi import HTTPException, status


class UserNotFoundByIdException(HTTPException):
    """User cannot be found by id"""

    def __init__(self):
        super().__init__(status_code=404,
                         detail=f"Active user by this id not "
                                f"found.")


class UserQueryIdMissmatchException(HTTPException):
    """
    Custom exception for when a query uuid and uuid in JWT is missmatch.
    """

    def __init__(self):
        super().__init__(status_code=404, detail=f"JWT token doesn't belong "
                                                 f"to requested user")


class ForgottenParametersException(HTTPException):
    """Custom exception for when a forgotten parameter is missing."""

    def __init__(self):
        super().__init__(status_code=422,
                         detail=f"Not all parameters was filled")
