from dataclasses import dataclass, fields, MISSING
from typing import Any, Dict, TypeVar, Union
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseDTO')


@dataclass
class BaseDTO:

    @classmethod
    def from_dict(
            cls: type[T],
            data: Dict[str, Any],
            strict: bool = False
    ) -> T:
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")

        class_fields = {f.name: f for f in fields(cls)}
        validated_data = {}
        skipped_fields = []

        for key, value in data.items():
            if key in class_fields:
                field = class_fields[key]
                try:
                    validated_value = cls._validate_field_value(
                        field_name=key,
                        field_type=field.type,
                        value=value
                    )
                    validated_data[key] = validated_value
                except (TypeError, ValueError) as e:
                    logger.warning(f"Error while validating field {key}: {e}")
                    if strict:
                        raise
                    skipped_fields.append(key)
            else:
                skipped_fields.append(key)
                if strict:
                    raise ValueError(f"Unknown field: {key}")

        if skipped_fields:
            logger.debug(
                f"Skipped fields for {cls.__name__}: {skipped_fields}")

        # Check for required fields
        required_fields = [
            f.name for f in fields(cls)
            if f.default == MISSING and f.default_factory == MISSING
        ]

        missing_fields = [field for field in required_fields if
                          field not in validated_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        return cls(**validated_data)

    @classmethod
    def from_object(
            cls: type[T],
            obj: Any,
            **extra_fields: Any
    ) -> T:
        data = {}

        # Extract fields from an object by field names
        for field in fields(cls):
            if hasattr(obj, field.name):
                data[field.name] = getattr(obj, field.name)

        # Add extra fields (for mapping or additional data)
        data.update(extra_fields)

        return cls.from_dict(data)

    @staticmethod
    def _validate_field_value(
            field_name: str,
            field_type: Any,
            value: Any
    ) -> Any:
        if value is None:
            if BaseDTO._is_optional_type(field_type):
                return None
            else:
                raise ValueError(f"Field {field_name} cannot be None")

        actual_type = BaseDTO._get_actual_type(field_type)

        if isinstance(value, actual_type):
            return value

        return BaseDTO._convert_value(field_name, actual_type, value)

    @staticmethod
    def _is_optional_type(field_type: Any) -> bool:
        return (
                hasattr(field_type, '__origin__') and
                field_type.__origin__ is Union and
                type(None) in field_type.__args__
        )

    @staticmethod
    def _get_actual_type(field_type: Any) -> Any:
        if BaseDTO._is_optional_type(field_type):
            return next(
                arg for arg in field_type.__args__ if arg is not type(None))
        return field_type

    @staticmethod
    def _convert_value(field_name: str, target_type: Any, value: Any) -> Any:
        try:
            if target_type in (str, int, float, bool):
                return target_type(value)

            if target_type.__name__ == 'Decimal':
                from decimal import Decimal
                return Decimal(str(value))

            if hasattr(target_type, '__bases__') and any(
                    base.__name__ == 'Enum' for base in target_type.__bases__
            ):
                if isinstance(value, str):
                    return target_type(value)
                elif isinstance(value, target_type):
                    return value

            logger.warning(
                f"Couldn't convert field {field_name} to {target_type}")
            return value

        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Couldn't convert field {field_name} to {target_type}: {e}")

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if exclude_none and value is None:
                continue
            result[field.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        class_fields = {f.name: f for f in fields(self)}

        for key, value in data.items():
            if key in class_fields:
                try:
                    validated_value = self._validate_field_value(
                        field_name=key,
                        field_type=class_fields[key].type,
                        value=value
                    )
                    setattr(self, key, validated_value)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Skipping field {key} update: {e}")