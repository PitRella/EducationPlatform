from enum import StrEnum


class UserAction(StrEnum):
    CREATE = "create"
    GET = "get"
    DELETE = "delete"
    UPDATE = "update"
