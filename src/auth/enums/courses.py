from enum import StrEnum


class AuthorAction(StrEnum):
    """Enum class representing author router actions in the system."""

    CREATE = 'create'
    GET = 'get'
    DELETE = 'delete'
    UPDATE = 'update'
