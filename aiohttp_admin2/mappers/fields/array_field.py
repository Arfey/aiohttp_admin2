import json
import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers import validators

__all__ = ["ArrayField", ]


class ArrayField(AbstractField):
    """
    A field for represent an array type:

    >>> from aiohttp_admin2.mappers import fields
    >>>
    >>> class Mapper(Mapper):
    >>>     field = fields.ArrayField(field_cls=fields.IntField)

    you need to specify `field_cls` which describe type of elements inside an
    array.
    """
    type_name: str = 'array'

    def __init__(
        self,
        *,
        field_cls: AbstractField,
        max_length: int = None,
        min_length: int = None,
        **kwargs: t.Any,
    ):
        super().__init__(**kwargs)
        self.field_cls = field_cls
        self.field = field_cls(value=None)

        if max_length or min_length:
            self.validators.append(
                validators.length(max_value=max_length, min_value=min_length)
            )

    def to_python(self) -> t.Optional[t.List[t.Any]]:
        if self._value:
            if isinstance(self._value, list):
                return [
                    self.field(i).to_python()
                    for i in self._value
                ]

            if not isinstance(self._value, str):
                raise ValidationError("Incorrect format for array field.")

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

    @property
    def failure_safe_value(self):
        if self._value:
            if isinstance(self._value, list):
                return self._value
            else:
                return self._value.split(',')
        return self._value

    def __call__(self, value: t.Any) -> "AbstractField":
        return self.__class__(
            field_cls=self.field_cls,
            required=self.required,
            validators=self.validators,
            default=self.default,
            primary_key=self.primary_key,
            value=value
        )

    def __repr__(self):
        return \
            f"{self.__class__.__name__}(name={self.type_name}," \
            f" value={self._value}), required={self.required}" \
            f" primary_key={self.primary_key}"\
            f" type={self.field_cls.__name__})"
