from fastapi import HTTPException


class WrongCredentialsException(HTTPException):
    """Custom exception for when wrong credentials are provided."""

    def __init__(self) -> None:
        """Initialize the WrongCredentialsException with status 404."""
        super().__init__(
            status_code=404,
            detail='User with this credentials can not be found',
        )


class AccessTokenExpiredException(HTTPException):
    """Custom exception for when an access token is expired."""

    def __init__(self) -> None:
        """Initialize the AccessTokenExpiredException with status 404."""
        super().__init__(status_code=404, detail='Access token expired')


class RefreshTokenException(HTTPException):
    """Custom exception for when a refresh token is invalid."""

    def __init__(self) -> None:
        """Initialize the RefreshTokenException with status 404."""
        super().__init__(
            status_code=404,
            detail='Cannot process refresh '
            'token. Probably token '
            "expired, doesn't exist or"
            ' attached to deleted user.',
        )
