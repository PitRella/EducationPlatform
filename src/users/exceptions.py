from fastapi import HTTPException


class UserNotFoundByIdException(HTTPException):
    """User cannot be found by id"""

    def __init__(self) -> None:
        super().__init__(
            status_code=404, detail="Active user by this id not found."
        )


class UserQueryIdMissmatchException(HTTPException):
    """
    Custom exception for when a query uuid and uuid in JWT is missmatch.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=404, detail="JWT token doesn't belong to requested user"
        )


class ForgottenParametersException(HTTPException):
    """Custom exception for when a forgotten parameter is missing."""

    def __init__(self) -> None:
        super().__init__(
            status_code=422, detail="Not all parameters was filled"
        )
