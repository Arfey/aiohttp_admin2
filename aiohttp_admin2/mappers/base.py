import typing as t
from abc import ABC

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers.fields.common_fields import EmptyValue
from aiohttp_admin2.mappers.exceptions import ValidationError


__all__ = ['Mapper', ]


# class AbstractMapper(ABC):
#     def is_valid(self):
#         return True
#
#
# class Mapper(AbstractMapper):
#     pass


class MapperMeta(type):
    """
    The main metaclass for all admin mappers.

    todo: abstract?
    """

    def __new__(mcs, name, bases, attrs):

        _fields_cls: t.List[AbstractField] = []
        new_attrs: t.Dict[str, t.Any] = {}

        for base in bases:
            if issubclass(base, Mapper) and getattr(base, '_fields_cls', None):
                _fields_cls.extend(base._fields_cls)

        for name, attr in attrs.items():
            if isinstance(attr, AbstractField):
                attr.name = name
                _fields_cls.append(attr)
            else:
                new_attrs[name] = attr

        new_attrs = {**new_attrs, "_fields_cls": _fields_cls}

        return super().__new__(mcs, name, bases, new_attrs)


class Mapper(metaclass=MapperMeta):
    _data: t.Dict[str, t.Any] = None
    _fields: t.Dict[str, AbstractField] = None

    def __init__(self, data: t.Dict[str, t.Any]) -> None:
        self._error: t.Optional[str] = None
        self._data = data
        self._fields = {
            field.name: field(data.get(field.name, EmptyValue()))
            for field in self._fields_cls
        }

    @property
    def fields(self) -> t.Dict[str, AbstractField]:
        return self._fields

    def is_valid(self) -> bool:
        is_valid = True

        for f in self.fields.values():
            try:
                f.is_valid()
            except ValidationError as e:
                print("name: ", f.name, "val: ", f.value, "err: ", e)
                is_valid = False
                if len(e.args):
                    f.error = e.args[0]
                else:
                    f.error = 'Invalid'

        # todo: mapper common validation

        return is_valid

    def __repr__(self):
        return f'{self.__class__.__name__}()'
