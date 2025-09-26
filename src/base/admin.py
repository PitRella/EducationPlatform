from typing import Any, ClassVar


class TimestampAdminMixin:
    """Mixin class for handling timestamp fields in the admin interface.

    This mixin provides basic configuration for handling
    created_at and updated_at timestamp fields in admin forms.
    It sets these fields as read-only and disabled
    to prevent manual modification of timestamps.

    Attributes:
        form_args: Class-level dictionary containing form field configurations
            for created_at and updated_at fields.

    """

    form_args: ClassVar[dict[str, Any]] = {
        'created_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'updated_at': {'render_kw': {'readonly': True, 'disabled': True}},
    }
