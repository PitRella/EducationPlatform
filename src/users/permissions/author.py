from abc import ABC

from fastapi.requests import Request

from src.base.permission import BasePermission
from src.users import Author
from src.users.exceptions import (
    UserPermissionException,
)


class BaseAuthorPermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            author: Author | None,
    ):
        super().__init__(request)
        self.author: Author | None = author

    def _is_author_authorized(self) -> Author:
        if not self.author:
            raise UserPermissionException
        return self.author
