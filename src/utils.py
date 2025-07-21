from typing import Any

from slugify import slugify


def make_slug(field: Any) -> str:
    """Return a slugified version of field.

    Args:
        field (Any): The value to be slugified.

    Returns:
        str: The slugified string.

    """
    return slugify(str(field))
