import typing as t
from dateutil import parser
from datetime import datetime
import json

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.exceptions import AdminException


__all__ = [
    "StringField",
    "IntField",
    "FloatField",
    "DateTimeField",
    "DateField",
    "BooleanField",
    "ChoicesField",
    "ArrayField",
    "JsonField",
]


class StringField(AbstractField):
    type_name: str = 'string'

    def to_python(self) -> t.Optional[str]:
        return str(self._value) if self._value else self._value


class IntField(AbstractField):
    type_name: str = 'int'

    def to_python(self) -> t.Optional[int]:
        return int(self._value) if self._value else self._value


class FloatField(AbstractField):
    type_name: str = 'float'

    def to_python(self) -> t.Optional[float]:
        return float(self._value) if self._value else self._value


class DateTimeField(AbstractField):
    type_name: str = 'datetime'

    def to_python(self) -> datetime:
        return parser.parse(self._value) if self._value else self._value


class DateField(AbstractField):
    type_name: str = 'date'

    def to_python(self) -> datetime:
        return parser.parse(self._value) if self._value else self._value


class BooleanField(AbstractField):
    type_name: str = 'boolean'
    false_values = ['0', 'false', 'f', '', 'none']

    def to_python(self) -> t.Optional[bool]:
        if str(self._value).lower() in self.false_values:
            return False

        return True


class ChoicesField(AbstractField):
    """
    This field will helpful if you have some finite list of values and want
    that this list will represented like select tag you need to use current
    field type.

    For that you need put list of values to choices parameter:

    choices = [
        (1, 'select'),
        (2, 'unselect'),
        (3, 'delete'),
    ]

    """
    type_name: str = 'choice'
    field: AbstractField

    def __init__(
        self,
        *,
        choices=None,
        field_cls=StringField,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.field_cls = field_cls
        # todo: if field_cls is object
        self.field = field_cls(**kwargs)
        self.choices = choices
        self._choice_validation(choices)

    def to_python(self) -> t.Optional[bool]:
        return self.field.to_python()

    def to_raw(self) -> str:
        return self.field.to_raw()

    def is_valid(self) -> bool:
        # todo: move to validator
        is_valid = self.field.is_valid()

        if not self.required and self.value is None:
            return is_valid

        if self.value in [str(value) for value, _ in self.choices]:
            return is_valid
        else:
            raise ValidationError(
                f"{self.__class__.__name__}.{self.name} has wrong value."
                f" It must be on of {[value for value, _ in self.choices]} "
                f"but received {self.value}"
            )

    def _choice_validation(self, choices):
        try:
            [(str(x), str(y)) for x, y in choices]
        except Exception:
            raise AdminException(
                f"`choices` parameter has wrong format for "
                f"{self.__class__.__name__}. It must be a tuple of tuples but "
                f"received {choices}."
            )

    def __call__(self, value: t.Any) -> AbstractField:

        if hasattr(value, 'name'):
            # handle enum case
            value = value.name

        return self.__class__(
            required=self.required,
            validators=self.validators,
            value=value,
            default=self.default,
            field_cls=self.field_cls,
            choices=self.choices,
        )


class ArrayField(AbstractField):
    type_name: str = 'array'
    # todo: min, max

    # todo: move to tags view

    def __init__(self, *, field_cls: AbstractField, **kwargs: t.Any):
        super().__init__(**kwargs)
        self.field_cls = field_cls
        self.field = field_cls(value=None)

    def to_python(self) -> t.Optional[t.List[t.Any]]:

        if self._value:
            if isinstance(self._value, list):
                return self._value
            if self._value.startswith('[') and self._value.endswith(']'):
                try:
                    return [
                        self.field(i).to_python()
                        for i in json.loads(self._value)
                    ]
                except json.decoder.JSONDecodeError:
                    raise ValidationError("Incorrect format for array field.")
            else:
                return [
                    self.field(i).to_python() for i in self._value.split(',')
                ]

        return self._value

    def __call__(self, value: t.Any) -> "AbstractField":
        return self.__class__(
            field_cls=self.field_cls,
            required=self.required,
            validators=self.validators,
            default=self.default,
            value=value
        )


class JsonField(AbstractField):
    type_name: str = 'json'

    def to_python(self) -> t.Optional[t.Dict[str, t.Any]]:

        if self._value:
            try:
                return json.loads(self._value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(
                    "Incorrect format for json field.")

        return self._value

    def to_raw(self) -> str:
        """
        Convert value to correct storage type.
        """
        if self._value is not None:
            try:
                if isinstance(self._value, dict):
                    return json.dumps(self._value, sort_keys=True, indent=4)
                else:
                    json.dumps(
                        json.loads(self._value), sort_keys=True, indent=4)
            except Exception:
                return str(self._value)

        return ""

# Todo: add other types
# Todo: add validators
# File
