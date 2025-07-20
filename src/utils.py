from typing import Any
from slugify import slugify

def make_slug(field: Any) -> str:
    return slugify(str(field))
