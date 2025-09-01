import json
from dataclasses import dataclass, fields, MISSING, is_dataclass
from typing import Any, Dict, List, TypeVar, Union, get_origin, get_args, \
    Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseDTO')


@dataclass
class BaseDTO:
    @classmethod
    def from_body(cls: type[T], body: bytes) -> T:
        return cls.from_dict(json.loads(body))

    @classmethod
    def from_dict(
            cls: type[T],
            data: Dict[str, Any],
            strict: bool = False
    ) -> T:
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")

        class_fields = {f.name: f for f in fields(cls)}
        validated_data: Dict[str, Any] = {}
        skipped_fields: List[str] = []

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
        data: Dict[str, Any] = {}

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

        # Handle nested dataclasses
        if is_dataclass(actual_type) and not isinstance(actual_type,
                                                        type(BaseDTO)):
            if isinstance(value, dict):
                return actual_type.from_dict(value) if hasattr(actual_type,
                                                               'from_dict') else actual_type(
                    **value)
            elif isinstance(value, actual_type):
                return value
            else:
                raise TypeError(
                    f"Cannot convert {type(value)} to {actual_type} for field {field_name}")

        # Handle BaseDTO subclasses
        if (isinstance(actual_type, type) and
                issubclass(actual_type, BaseDTO) and
                actual_type is not BaseDTO):
            if isinstance(value, dict):
                return actual_type.from_dict(value)
            elif isinstance(value, actual_type):
                return value
            else:
                raise TypeError(
                    f"Cannot convert {type(value)} to {actual_type} for field {field_name}")

        # Handle generic types (List, Dict, etc.)
        origin = get_origin(actual_type)
        if origin is not None:
            return BaseDTO._handle_generic_type(field_name, actual_type, value)

        # Handle primitive types and enums
        if isinstance(value, actual_type):
            return value

        return BaseDTO._convert_value(field_name, actual_type, value)

    @staticmethod
    def _handle_generic_type(field_name: str, field_type: Any,
                             value: Any) -> Any:
        origin = get_origin(field_type)
        type_args = get_args(field_type)

        if origin is list or origin is List:
            if not isinstance(value, list):
                raise TypeError(
                    f"Expected list for field {field_name}, got {type(value)}")

            if not type_args:
                return value

            element_type = type_args[0]
            converted_list: List[Any] = []

            for i, item in enumerate(value):
                try:
                    converted_item = BaseDTO._validate_field_value(
                        field_name=f"{field_name}[{i}]",
                        field_type=element_type,
                        value=item
                    )
                    converted_list.append(converted_item)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Error converting list item at index {i} for field {field_name}: {e}")

            return converted_list

        elif origin is dict or origin is Dict:
            if not isinstance(value, dict):
                raise TypeError(
                    f"Expected dict for field {field_name}, got {type(value)}")

            if len(type_args) < 2:
                return value

            key_type, value_type = type_args[0], type_args[1]
            converted_dict: Dict[Any, Any] = {}

            for k, v in value.items():
                try:
                    converted_key = BaseDTO._validate_field_value(
                        field_name=f"{field_name}.key",
                        field_type=key_type,
                        value=k
                    )
                    converted_value = BaseDTO._validate_field_value(
                        field_name=f"{field_name}[{k}]",
                        field_type=value_type,
                        value=v
                    )
                    converted_dict[converted_key] = converted_value
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Error converting dict item for key {k} in field {field_name}: {e}")

            return converted_dict

        else:
            # For other generic types, just return the value as-is
            logger.warning(
                f"Unsupported generic type {origin} for field {field_name}")
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

            if hasattr(target_type,
                       '__name__') and target_type.__name__ == 'Decimal':
                from decimal import Decimal
                return Decimal(str(value))

            # Handle enums
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
        result: Dict[str, Any] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if exclude_none and value is None:
                continue

            # Recursively convert nested dataclasses to dict
            if is_dataclass(value) and not isinstance(value, type):
                if hasattr(value, 'to_dict'):
                    result[field.name] = value.to_dict(
                        exclude_none=exclude_none)
                else:
                    # For regular dataclasses without to_dict method
                    nested_dict: Dict[str, Any] = {}
                    for nested_field in fields(value):
                        nested_value = getattr(value, nested_field.name)
                        if exclude_none and nested_value is None:
                            continue
                        nested_dict[nested_field.name] = nested_value
                    result[field.name] = nested_dict
            elif isinstance(value, list):
                converted_list: List[Any] = []
                for item in value:
                    if is_dataclass(item) and not isinstance(item, type):
                        if hasattr(item, 'to_dict'):
                            converted_list.append(
                                item.to_dict(exclude_none=exclude_none))
                        else:
                            item_dict: Dict[str, Any] = {}
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
                converted_dict: Dict[str, Any] = {}
                for k, v in value.items():
                    if is_dataclass(v) and not isinstance(v, type):
                        if hasattr(v, 'to_dict'):
                            converted_dict[k] = v.to_dict(
                                exclude_none=exclude_none)
                        else:
                            v_dict: Dict[str, Any] = {}
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
