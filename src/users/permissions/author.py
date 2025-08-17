from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users import Author
from src.users.exceptions import (
    UserPermissionException,
)


class BaseAuthorPermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.author: Author | None = kwargs.get('author')

    def _is_author_authorized(self) -> Author:
        if not self.author:
            raise UserPermissionException
        return self.author
