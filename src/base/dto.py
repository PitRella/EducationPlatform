import json
import logging
from dataclasses import MISSING, dataclass, fields, is_dataclass
from decimal import Decimal
from typing import (
    Any,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseDTO')
_NUMBER_OF_TYPE_ARGS: int = 2


@dataclass
class BaseDTO:
    """Base Data Transfer Object class providing serialization and validation.

    This class serves as a foundation for creating DTOs with automatic
    serialization, deserialization, and validation capabilities. It supports:
    - JSON serialization/deserialization
    - Dictionary conversion (to/from)
    - Nested dataclass handling
    - Type validation and conversion
    - Optional field handling
    - Strict mode for validation
    - Object mapping

    Example:
        @dataclass
        class UserDTO(BaseDTO):
            name: str
            age: int
            email: str | None = None

        # Create from dict
        user = UserDTO.from_dict({"name": "John", "age": "25"})

        # Convert to dict
        data = user.to_dict()

        # Update from dict
        user.update_from_dict({"age": 26})

    """

    @classmethod
    def from_body(cls: type[T], body: bytes) -> T:
        """Create a DTO instance from bytes containing JSON data.

        Args:
            body (bytes): Raw bytes containing JSON-encoded data.

        Returns:
            T: New instance of the DTO class populated with data from the JSON.

        Raises:
            json.JSONDecodeError: If the body cannot be decoded as JSON.
            TypeError: If the decoded JSON is not a dictionary.
            ValueError: If required fields are missing or validation fails.

        """
        return cls.from_dict(json.loads(body))

    @classmethod
    def from_dict(
        cls: type[T],
        data: dict[str, Any],
        strict: bool = False,  # noqa: FBT001, FBT002
    ) -> T:
        """Create a DTO instance from a dictionary.

        Validates and converts dictionary data to create a new instance of the
        DTO class. Performs type validation and conversion for all fields.

        Args:
            data (dict[str, Any]): Dictionary with field names and values.
            strict (bool, optional): If True, raises exceptions for unknown
                fields and validation errors. If False, skips invalid fields
                with warnings. Defaults to False.

        Returns:
            T: New instance of the DTO class populated with validated data.

        Raises:
            TypeError: If data is not a dictionary or field conversion fails.
            ValueError: If required fields are missing or validation fails in
                strict mode.

        """
        if not isinstance(data, dict):
            raise TypeError('Data must be a dictionary')  # noqa: TRY003

        class_fields = {f.name: f for f in fields(cls)}
        validated_data: dict[str, Any] = {}
        skipped_fields: list[str] = []

        for key, value in data.items():
            if key in class_fields:
                field = class_fields[key]
                try:
                    validated_value = cls._validate_field_value(
                        field_name=key, field_type=field.type, value=value
                    )
                    validated_data[key] = validated_value
                except (TypeError, ValueError) as e:
                    logger.warning(
                        'Error while validating field %s: %s', key, e
                    )
                    if strict:
                        raise
                    skipped_fields.append(key)
            else:
                skipped_fields.append(key)
                if strict:
                    raise ValueError('Unknown field: %s', key) from None  # noqa: TRY003

        if skipped_fields:
            logger.debug(
                'Skipped fields for %s %s', cls.__name__, skipped_fields
            )

        # Check for required fields
        required_fields = [
            f.name
            for f in fields(cls)
            if f.default == MISSING and f.default_factory == MISSING
        ]

        missing_fields = [
            field for field in required_fields if field not in validated_data
        ]
        if missing_fields:
            raise ValueError('Missing required fields: %s', missing_fields)  # noqa: TRY003

        return cls(**validated_data)

    @classmethod
    def from_object(cls: type[T], obj: Any, **extra_fields: Any) -> T:
        """Create a DTO instance by mapping fields from another object.

        Creates a new DTO instance by copying field values from the provided
        object that match the DTO's field names. Additional fields can be
        provided through extra_fields.

        Args:
            obj (Any): Source object to extract field values from.
            **extra_fields (Any): Additional field values to include in the
                created DTO.

        Returns:
            T: New instance of the DTO class populated with values from the
                source object and extra fields.

        Example:
            class UserModel:
                def __init__(self):
                    self.name = "John"
                    self.age = 30

            @dataclass
            class UserDTO(BaseDTO):
                name: str
                age: int
                role: str

            user_model = UserModel()
            user_dto = UserDTO.from_object(user_model, role="admin")

        """
        data: dict[str, Any] = {}

        # Extract fields from an object by field names
        for field in fields(cls):
            if hasattr(obj, field.name):
                data[field.name] = getattr(obj, field.name)

        # Add extra fields (for mapping or additional data)
        data.update(extra_fields)

        return cls.from_dict(data)

    @staticmethod
    def _validate_field_value(  # noqa: C901, PLR0911
        field_name: str, field_type: Any, value: Any
    ) -> Any:
        if value is None:
            if BaseDTO._is_optional_type(field_type):
                return None
            raise ValueError('Field %s cannot be None', field_name)  # noqa: TRY003

        actual_type = BaseDTO._get_actual_type(field_type)

        # Handle nested dataclasses
        if is_dataclass(actual_type) and not isinstance(
            actual_type, type(BaseDTO)
        ):
            if isinstance(value, dict):
                return (
                    actual_type.from_dict(value)
                    if hasattr(actual_type, 'from_dict')
                    else actual_type(**value)  # type: ignore
                )
            if isinstance(value, actual_type):  # type: ignore
                return value
            raise TypeError(  # noqa: TRY003
                'Cannot convert %s to %s for field %s',
                type(value),
                actual_type,
                field_name,
            )

        # Handle BaseDTO subclasses
        if (
            isinstance(actual_type, type)
            and issubclass(actual_type, BaseDTO)
            and actual_type is not BaseDTO
        ):
            if isinstance(value, dict):
                return actual_type.from_dict(value)
            if isinstance(value, actual_type):
                return value
            raise TypeError(  # noqa: TRY003
                'Cannot convert %s to %s for field %s',
                type(value),
                actual_type,
                field_name,
            )
        # Handle generic types (List, Dict, etc.)
        origin = get_origin(actual_type)
        if origin is not None:
            return BaseDTO._handle_generic_type(field_name, actual_type, value)

        # Handle primitive types and enums
        if isinstance(value, actual_type):
            return value

        return BaseDTO._convert_value(field_name, actual_type, value)

    @staticmethod
    def _handle_generic_type(  # noqa: C901
        field_name: str, field_type: Any, value: Any
    ) -> Any:
        origin = get_origin(field_type)
        type_args = get_args(field_type)

        if origin is list or origin is list:
            if not isinstance(value, list):
                raise TypeError(  # noqa: TRY003
                    'Expected list for field %s, got %s',
                    field_name,
                    type(value),
                )

            if not type_args:
                return value

            element_type = type_args[0]
            converted_list: list[Any] = []

            for i, item in enumerate(value):
                try:
                    converted_item = BaseDTO._validate_field_value(
                        field_name=f'{field_name}[{i}]',
                        field_type=element_type,
                        value=item,
                    )
                    converted_list.append(converted_item)
                except (TypeError, ValueError) as e:
                    raise TypeError(  # noqa: TRY003
                        'Error converting list item at index %s for field %s %s',  # noqa: E501
                        i,
                        field_name,
                        e,
                    ) from None

            return converted_list

        if origin is dict or origin is dict:
            if not isinstance(value, dict):
                raise TypeError(  # noqa: TRY003
                    'Expected dict for field %s, got %s',
                    field_name,
                    type(value),
                )

            if len(type_args) < _NUMBER_OF_TYPE_ARGS:
                return value

            key_type, value_type = type_args[0], type_args[1]
            converted_dict: dict[Any, Any] = {}

            for k, v in value.items():
                try:
                    converted_key = BaseDTO._validate_field_value(
                        field_name=f'{field_name}.key',
                        field_type=key_type,
                        value=k,
                    )
                    converted_value = BaseDTO._validate_field_value(
                        field_name=f'{field_name}[{k}]',
                        field_type=value_type,
                        value=v,
                    )
                    converted_dict[converted_key] = converted_value
                except (TypeError, ValueError) as e:
                    raise TypeError(  # noqa: TRY003
                        'Error converting dict item for key %s in field %s: %s',
                        k,
                        field_name,
                        e,
                    ) from None

            return converted_dict

        # For other generic types, just return the value as-is
        logger.warning(
            'Unsupported generic type %s for field %s', origin, field_name
        )
        return value

    @staticmethod
    def _is_optional_type(field_type: Any) -> bool:
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            return type(None) in args
        return False

    @staticmethod
    def _get_actual_type(field_type: Any) -> Any:
        if BaseDTO._is_optional_type(field_type):
            args = get_args(field_type)
            return next(arg for arg in args if arg is not type(None))
        return field_type

    @staticmethod
    def _convert_value(field_name: str, target_type: Any, value: Any) -> Any:
        try:
            if target_type in (str, int, float, bool):
                return target_type(value)

            if (
                hasattr(target_type, '__name__')
                and target_type.__name__ == 'Decimal'
            ):
                return Decimal(str(value))

            # Handle enums
            if hasattr(target_type, '__bases__') and any(
                base.__name__ == 'Enum' for base in target_type.__bases__
            ):
                if isinstance(value, str):
                    return target_type(value)
                if isinstance(value, target_type):
                    return value
            else:
                logger.warning(
                    "Couldn't convert field %s to %s", field_name, target_type
                )
                return value

        except (ValueError, TypeError) as e:
            raise TypeError(  # noqa: TRY003
                "Couldn't convert field %s to %s: %s",
                field_name,
                target_type,
                e,
            ) from None

    def to_dict(self, *, exclude_none: bool = False) -> dict[str, Any]:  # noqa: C901, PLR0912
        """Convert the DTO instance to a dictionary representation.

        Recursively converts all nested dataclasses, lists, and dictionaries
        to their dictionary representations. For nested dataclasses, it will
        attempt to use their to_dict method if available, otherwise it will
        create a dictionary from their fields directly.

        Args:
            exclude_none (bool, optional): If True, fields with None values
                will be excluded from the resulting dictionary. Defaults to
                False.

        Returns:
            dict[str, Any]: Dictionary containing all fields of the DTO and
                their values, with nested structures converted to dictionaries.

        """
        result: dict[str, Any] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if exclude_none and value is None:
                continue

            # Recursively convert nested dataclasses to dict
            if is_dataclass(value) and not isinstance(value, type):
                if hasattr(value, 'to_dict'):
                    result[field.name] = value.to_dict(
                        exclude_none=exclude_none
                    )
                else:
                    # For regular dataclasses without to_dict method
                    nested_dict: dict[str, Any] = {}
                    for nested_field in fields(value):
                        nested_value = getattr(value, nested_field.name)
                        if exclude_none and nested_value is None:
                            continue
                        nested_dict[nested_field.name] = nested_value
                    result[field.name] = nested_dict
            elif isinstance(value, list):
                converted_list: list[Any] = []
                for item in value:
                    if is_dataclass(item) and not isinstance(item, type):
                        if hasattr(item, 'to_dict'):
                            converted_list.append(
                                item.to_dict(exclude_none=exclude_none)
                            )
                        else:
                            item_dict: dict[str, Any] = {}
                            for item_field in fields(item):
                                item_value = getattr(item, item_field.name)
                                if exclude_none and item_value is None:
                                    continue
                                item_dict[item_field.name] = item_value
                            converted_list.append(item_dict)
                    else:
                        converted_list.append(item)
                result[field.name] = converted_list
            elif isinstance(value, dict):
                converted_dict: dict[str, Any] = {}
                for k, v in value.items():
                    if is_dataclass(v) and not isinstance(v, type):
                        if hasattr(v, 'to_dict'):
                            converted_dict[k] = v.to_dict(
                                exclude_none=exclude_none
                            )
                        else:
                            v_dict: dict[str, Any] = {}
                            for v_field in fields(v):
                                v_value = getattr(v, v_field.name)
                                if exclude_none and v_value is None:
                                    continue
                                v_dict[v_field.name] = v_value
                            converted_dict[k] = v_dict
                    else:
                        converted_dict[k] = v
                result[field.name] = converted_dict
            else:
                result[field.name] = value

        return result

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update the DTO instance with values from a dictionary.

        Updates only fields that exist in the DTO class. Values are validated
        using the same validation rules as in from_dict method. Invalid values
        are skipped with a warning.

        Args:
            data (dict[str, Any]): Dictionary containing field names and values
                to update.

        """
        class_fields = {f.name: f for f in fields(self)}

        for key, value in data.items():
            if key in class_fields:
                try:
                    validated_value = self._validate_field_value(
                        field_name=key,
                        field_type=class_fields[key].type,
                        value=value,
                    )
                    setattr(self, key, validated_value)
                except (TypeError, ValueError) as e:
                    logger.warning('Skipping field %s update: %s', key, e)
