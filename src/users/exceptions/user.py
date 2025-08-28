from fastapi import HTTPException


class UserNotAuthorizedException(HTTPException):
    """Exception raised when a user is not authorized."""

    def __init__(self) -> None:
        """Initialize UserNotAuthorizedException with status 401."""
        super().__init__(
            status_code=401,
            detail='User not authorized',
        )


class UserNotFoundByIdException(HTTPException):
    """Exception raised when a user cannot be found by ID."""

    def __init__(self) -> None:
        """Initialize UserNotFoundByIdException with status 404."""
        super().__init__(
            status_code=404,
            detail='Active user by this id not found.',
        )


class ForgottenParametersException(HTTPException):
    """Exception raised when required parameters are missing."""

    def __init__(self) -> None:
        """Initialize ForgottenParametersException with status 422."""
        super().__init__(
            status_code=422,
            detail='Not all parameters were filled',
        )


class BadEmailSchemaException(HTTPException):
    """Exception raised for invalid email format."""

    def __init__(self) -> None:
        """Initialize BadEmailSchemaException with status 422."""
        super().__init__(
            status_code=422,
            detail='Invalid email address. Make sure it contains only '
            'valid characters.',
        )


class BadPasswordSchemaException(HTTPException):
    """Exception raised for invalid password format."""

    def __init__(self) -> None:
        """Initialize BadPasswordSchemaException with status 422."""
        super().__init__(
            status_code=422,
            detail='Password should contain at least one uppercase letter, '
            'one lowercase letter, one digit, and one special '
            'character @$!%*?&.',
        )


class UserPermissionException(HTTPException):
    """Exception raised when a user lacks permission for an action."""

    def __init__(self) -> None:
        """Initialize UserPermissionException with status 404."""
        super().__init__(
            status_code=404,
            detail="This user doesn't have permission to do this action",
        )
