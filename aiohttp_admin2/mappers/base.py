import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.exceptions import MapperError


__all__ = ['Mapper', ]


class MapperMeta(type):
    """
    The main metaclass for all admin mappers.

    todo: abstract?
    """

    def __new__(mcs, name, bases, attrs, **kwargs):

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

        return super().__new__(mcs, name, bases, new_attrs, **kwargs)


class Mapper(metaclass=MapperMeta):

    _data: t.Dict[str, t.Any] = None
    _fields: t.Dict[str, AbstractField] = None

    def __init__(self, data: t.Dict[str, t.Any]) -> None:
        self._pass_validation = False
        self.with_errors = False
        self.error: t.Optional[str] = None
        self._data = data
        self._fields = self._fields or {}
        self._fields_after_validation = []
        for field in self._fields_cls:
            new_field = field(data.get(field.name))
            new_field.name = field.name
            self._fields[field.name] = new_field

    @property
    def raw_data(self):
        """Getter for raw mapper data"""
        return self._data

    @property
    def data(self) -> t.Dict[str, t.Any]:
        """Return serialize data"""
        if not self._pass_validation:
            raise MapperError(
                "Try to get data from mapper before call the `is_valid` "
                "method."
            )
        return {
            f.name: f.to_python()
            for f in self._fields_after_validation
        }

    @property
    def fields(self) -> t.Dict[str, AbstractField]:
        return self._fields

    def validation(self):
        """
        This method need to give simple approach for user add custom validation
        for mapper. Error which will raise here will add as mapper error. It
        can be helpful if we want to check validate data in few fields
        together not in single field.

        Raises:
            ValidationError: if value is invalid
        """
        pass

    def is_valid(self, skip_primary: bool = False) -> bool:
        """
        This method need to called for check if mapper data is valid. It run
        validators for each field and main validator for mapper.

        Also it run custom validators for field if these are defined:

        >>> class Book(Mapper):
        >>>    name = fields.StringField()
        >>>
        >>>    def validation_name(self, value):
        >>>        if len(value) < 10:
        >>>            raise ValidationError("name is to short")

        For that you need define function which has name start with
        `validation_` and end with name of field which you want to validate.
        This function must receive value as parameter and raise ValidationError
        if it is invalid.

        If we set `skip_primary` to `True` then a mapper will not to check the
        primary key field.
        """
        is_valid = True

        if self._pass_validation:
            # if we'll call is_valid method more than once with wrong data
            # than errors will duplicate
            raise MapperError(
                "`is_valid` method have to call only once per life cycle of "
                "the mapper object"
            )

        for f in self.fields.values():

            if skip_primary and f.primary_key:
                continue

            self._fields_after_validation.append(f)

            f.apply_default_if_need()
            try:
                f.is_valid()
                validator_name = f'validation_{f.name}'
                if hasattr(self, validator_name):
                    getattr(self, validator_name)(f.to_python())
            except (ValidationError, TypeError) as e:
                is_valid = False
                if len(e.args):
                    f.errors.append(e.args[0])
                else:
                    f.errors.append('Invalid')

        try:
            self.validation()
        except ValidationError as e:
            is_valid = False
            if len(e.args):
                self.error = e.args[0]
            else:
                if not self.error:
                    self.error = 'Invalid'

        self.with_errors = not is_valid
        self._pass_validation = True

        return is_valid

    def __repr__(self):
        return f'{self.__class__.__name__}()'
