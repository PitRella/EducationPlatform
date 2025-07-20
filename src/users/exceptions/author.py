from fastapi import HTTPException


class AdminCannotBeAuthorException(HTTPException):
    """Admin cannot be author."""

    def __init__(self) -> None:
        """Initialize the AdminCannotBeAuthorException with status 404."""
        super().__init__(
            status_code=404,
            detail='Superadmin/Admin cannot become author.',
        )


class UserIsNotAuthorException(HTTPException):
    """User is not an author."""

    def __init__(self) -> None:
        """Initialize the UserIsNotAuthorException with status 404."""
        super().__init__(
            status_code=404,
            detail='Verified author not found by this credentials.',
        )
