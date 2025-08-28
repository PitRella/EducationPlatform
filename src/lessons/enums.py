from enum import StrEnum


class LessonTypeEnum(StrEnum):
    """Enumeration of available lesson types in the system.

    Defines the valid types that can be assigned to a lesson, ensuring
    consistent type identification across the application.
    """

    VIDEO = 'VIDEO'
    QUIZ = 'QUIZ'
    TEXT = 'TEXT'
    PRACTICE = 'PRACTICE'
