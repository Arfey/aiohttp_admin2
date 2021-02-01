import typing as t
from dateutil import parser
from datetime import datetime
import json
import re

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
    "UrlField",
    "UrlFileField",
    "UrlImageField",
]


class StringField(AbstractField):
    type_name: str = 'string'

    def to_python(self) -> t.Optional[str]:
        return str(self._value) if self._value else self._value


class IntField(AbstractField):
    type_name: str = 'int'

    def to_python(self) -> t.Optional[int]:
        try:
            return int(self._value) if self._value else self._value
        except ValueError:
            raise ValidationError("Incorrect value for Int field.")


class FloatField(AbstractField):
    type_name: str = 'float'

    def to_python(self) -> t.Optional[float]:
        return float(self._value) if self._value else self._value


class DateTimeField(AbstractField):
    type_name: str = 'datetime'

    def to_python(self) -> datetime:
        try:
            return parser.parse(self._value) if self._value else None
        except parser.ParserError:
            raise ValidationError("Incorrect format for time field.")


class DateField(DateTimeField):
    type_name: str = 'date'


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
    empty_value: str = '-- empty --'
    field: AbstractField

    def __init__(
        self,
        *,
        choices=None,
        field_cls=StringField,
        empty_value: str = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.field_cls = field_cls
        # todo: if field_cls is object
        self.field = field_cls(**kwargs)
        self.empty_value = \
            self.empty_value if empty_value is None else empty_value
        self.choices = choices
        self._choice_validation(choices)

    def to_python(self) -> t.Optional[bool]:
        value = self.field.to_python()

        if value == '':
            return None

        return value

    def to_storage(self) -> str:
        return self.field.to_storage()

    def is_valid(self) -> bool:
        # todo: move to validator
        is_valid = self.field.is_valid()

        if not self.required and self.value is None:
            return is_valid

        if self.value in [str(value) for value, _ in self.choices]:
            return is_valid
        else:
            raise ValidationError(
                f"{self.__class__.__name__} has wrong value."
                f" It must be on of {[value for value, _ in self.choices]} "
                f"but received '{self.value}'"
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

    def __init__(self, *, field_cls: AbstractField, **kwargs: t.Any):
        super().__init__(**kwargs)
        self.field_cls = field_cls
        self.field = field_cls(value=None)

    def to_python(self) -> t.Optional[t.List[t.Any]]:
        # todo: add validation for inner type

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
        if self._value.strip():
            try:
                return json.loads(self._value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(
                    "Incorrect format for json field.")

        return self._value

    def to_storage(self) -> str:
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
                return str(self._value).strip()

        return ""


class UrlField(StringField):
    type_name: str = 'url'

    URL_REGEXP = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:\S+(?::\S*)?@)?'  # user and password
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-_]{0,61}[A-Z0-9])?\.)'
        r'+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE,
    )

    def is_valid(self) -> bool:
        is_valid = super().is_valid()

        if is_valid and self._value:
            if not self.URL_REGEXP.match(self.value):
                raise ValidationError(f"{self.value} is not valid url.")

        return is_valid


class UrlFileField(StringField):
    type_name: str = 'url_file'

    def to_python(self) -> t.Optional[str]:
        if self._value and not hasattr(self._value, 'file'):
            return str(self._value)

        return self._value


class UrlImageField(UrlFileField):
    type_name: str = 'url_file_image'

    def to_python(self) -> t.Optional[str]:
        if self._value and not hasattr(self._value, 'file'):
            if self._value in ('None', 'on'):
                return None

            return str(self._value)

        return self._value

# Todo: add other types
# Todo: add validators
# File
