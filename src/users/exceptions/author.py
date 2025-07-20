from fastapi import HTTPException


class AdminCannotBeAuthorException(HTTPException):
    """User cannot be found by id."""

    def __init__(self) -> None:
        """Initialize the AdminCannotBeAuthorException with status 404."""
        super().__init__(
            status_code=404,
            detail='Superadmin/Admin cannot become author.',
        )