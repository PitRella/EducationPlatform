from fastapi import HTTPException


class UserNotFoundByIdException(HTTPException):
    """User cannot be found by id."""

    def __init__(self) -> None:
        """Initialize the UserNotFoundByIdException with status 404."""
        super().__init__(
            status_code=404,
            detail='Active user by this id not found.',
        )


class UserQueryIdMissmatchException(HTTPException):
    """Custom exception for when a query uuid and uuid in JWT is missmatch."""

    def __init__(self) -> None:
        """Initialize the UserQueryIdMissmatchException with status 404."""
        super().__init__(
            status_code=404,
            detail="JWT token doesn't belong to requested user",
        )


class ForgottenParametersException(HTTPException):
    """Custom exception for when a forgotten parameter is missing."""

    def __init__(self) -> None:
        """Initialize the ForgottenParametersException with status 422."""
        super().__init__(
            status_code=422,
            detail='Not all parameters was filled',
        )


class BadEmailException(HTTPException):
    """Custom exception for when an email is incorrect."""

    def __init__(self) -> None:
        """Initialize the BadEmailException with status 422."""
        super().__init__(
            status_code=422, detail='Email does not fill requirements.'
        )


class BadPasswordException(HTTPException):
    """Custom exception for when a password is incorrect."""

    def __init__(self) -> None:
        """Initialize the BadPasswordException with status 422."""
        super().__init__(
            status_code=422,
            detail='Password should contain at least one uppercase letter,'
            ' one lowercase letter,'
            ' one digit and one special character @$!%*?&.',
        )
