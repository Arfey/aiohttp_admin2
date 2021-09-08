import typing as t

from aiohttp_admin2.exceptions import AdminException
from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers.fields.string_field import StringField

__all__ = ["ChoicesField", ]


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

    >>> from aiohttp_admin2.mappers import fields
    >>>
    >>> choices = [(1, 'select'), (2, 'unselect'), ]
    >>>
    >>> class Mapper(Mapper):
    >>>     field = type = fields.ChoicesField(
    >>>         field_cls=fields.StringField,
    >>>         choices=choices,
    >>>     )

    you need to specify `field_cls` which describe type of field. By default
    it's a `StringField`.
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
        self.default = kwargs.get('default')
        self._choice_validation(choices)

    def to_python(self) -> t.Optional[bool]:
        value = self.field.to_python()

        if value == '':
            return None

        return value

    def to_storage(self) -> str:
        return self.field.to_storage()

    def is_valid(self) -> bool:
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

    def apply_default_if_need(self):
        super().apply_default_if_need()
        self.field.apply_default_if_need()

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
            primary_key=self.primary_key,
        )
