from enum import StrEnum


class UserAction(StrEnum):
    CREATE = "create"
    GET = "get"
    DELETE = "delete"
    UPDATE = "update"
    SET_ADMIN_PRIVILEGE = "set_admin_privilege"
