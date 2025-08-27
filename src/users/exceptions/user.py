from fastapi import HTTPException


class UserNotAuthorizedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail='User not authorized',
        )


class UserNotFoundByIdException(HTTPException):
    """User cannot be found by id."""

    def __init__(self) -> None:
        """Initialize the UserNotFoundByIdException with status 404."""
        super().__init__(
            status_code=404,
            detail='Active user by this id not found.',
        )


class ForgottenParametersException(HTTPException):
    """Custom exception for when a forgotten parameter is missing."""

    def __init__(self) -> None:
        """Initialize the ForgottenParametersException with status 422."""
        super().__init__(
            status_code=422,
            detail='Not all parameters was filled',
        )


class BadEmailSchemaException(HTTPException):
    """Custom exception for when an email is incorrect."""

    def __init__(self) -> None:
        """Initialize the BadEmailException with status 422."""
        super().__init__(
            status_code=422,
            detail='Invalid email address.'
            ' Make sure it contains only valid characters.',
        )


class BadPasswordSchemaException(HTTPException):
    """Custom exception for when a password is incorrect."""

    def __init__(self) -> None:
        """Initialize the BadPasswordException with status 422."""
        super().__init__(
            status_code=422,
            detail='Password should contain at least one uppercase letter,'
            ' one lowercase letter,'
            ' one digit and one special character @$!%*?&.',
        )


class UserPermissionException(HTTPException):
    """Custom exception for when a user doesn't have permission."""

    def __init__(self) -> None:
        """Initialize the UserPermissionException with status 404."""
        super().__init__(
            status_code=404,
            detail="This user doesn't have permission to do this action",
        )
