from enum import StrEnum


class CourseLevelEnum(StrEnum):
    """Enum class representing course levels in the system."""

    BASIC = 'basic'  # For user just starting learning
    MEDIUM = 'medium'  # For user with intermediate knowledge
    PROFESSIONAL = 'professional'  # For user with advanced knowledge


class CurrencyEnum(StrEnum):
    """Enum class representing currencies in the system."""

    USD = 'usd'
    EUR = 'eur'


class AvailableLanguagesEnum(StrEnum):
    """Enum class representing available languages for course."""

    EN = 'en'  # English
    DE = 'de'  # Deutsch
    FR = 'fr'  # French
