from enum import StrEnum


class UserAction(StrEnum):
    CREATE = "create"
    GET = "get"
    DELETE = "delete"
    UPDATE = "update"
    SET_ADMIN_PRIVILEGE = "set_admin_privilege"
    REVOKE_ADMIN_PRIVILEGE = "revoke_admin_privilege"
