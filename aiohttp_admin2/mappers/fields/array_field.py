import json
import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["ArrayField", ]


class ArrayField(AbstractField):
    type_name: str = 'array'
    # todo: min, max

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
