from typing import (
    List,
    Any,
    Dict,
    Optional,
)
from copy import deepcopy

from aiohttp_admin2.core.fields.abc import FieldABC
from aiohttp_admin2.core.constants import FormError
from aiohttp import web


__all__ = ['FormMeta', 'BaseForm', ]


FORM_ERROR = '''
<p class='error'>{message}</p>
'''

BASE_FORM_TEMPALTE = '''
<form method="{method}">
    {main}
    <input type="submit" value="submit"/>
    {errors}
</form>
'''


class FormMeta(type):
    """
    Metaclass for all admin forms.
    """
    def __new__(mcs, name, bases, attrs, **kwargs):
        fields = {}
        new_attrs = {}

        for key, value in attrs.items():
            if isinstance(value, FieldABC):
                value.name = key
                fields.update({key: value})
            else:
                new_attrs.update({key: value})
        
        new_attrs['_class_fields'] = fields
        if new_attrs.get('Meta'):
            new_attrs['_meta'] = attrs['Meta'].__dict__
        else:
            new_attrs['_meta'] = {}
        
        new_class = super().__new__(mcs, name, bases, new_attrs, **kwargs)

        fields = {}
        meta = {}

        for class_obj in reversed(new_class.__mro__):
            if hasattr(class_obj, '_class_fields'):
                fields.update(class_obj._class_fields)

            if hasattr(class_obj, '_meta'):
                meta.update(class_obj._meta)

        new_class._class_fields = fields
        new_class._meta = meta

        return new_class


class BaseForm(metaclass=FormMeta):
    """
    The base class for all admin forms.
    """
    is_check = False

    def __init__(self, data: Optional[Dict[str, str]] = None) -> None:
        print('here 2 ********************')
        self._fields = deepcopy(self._class_fields)
        self.form_errors: List[FormError] = []
        if data:
            for name, value in data.items():
                try:
                    self._fields[name]._set_value(value)
                except KeyError:
                    raise KeyError(
                        f'Key {name} not found in {self.__class__.__name__}. '
                        f'Use one of these fields: '
                        f'{", ".join([f.name for f in self._fields])}'
                    )

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __getitem__(self, name: str) -> Any:
        try:
            value = self._fields[name].value
        except KeyError:
            raise KeyError(
                f'Key {name} not found in {self.__class__.__name__}. '
                f'Use one of these fields: '
                f'{", ".join([f.name for f in self._fields])}'
            )
        
        return value

    def render_to_html(self) -> str:
        """
        This method generate html code for create / edit form in admin
        interface. If instance is not empty form will be with predefine inputs.
        """

        ctx = {
            'method': self._meta['method'],
            'main': '',
            'errors': '',
        }

        for field in self._fields.values():
            ctx['main'] += field.render_to_html()
        
        if self.is_check:
            if self.form_errors:
                ctx['errors'] = "".join([
                    FORM_ERROR.format(err.message)
                    for err in self.form_errors
                ])

        return self._meta['template'].format(**ctx)

    def is_valid(self) -> bool:
        """
        This method provide validation for form and must be call before save.
        """
        is_valid = True

        for field in self._fields.values():
            if not field.is_valid:
                is_valid = False
        
        self.validation()
        self.is_check = True

        return is_valid and not bool(self.form_errors)

    def validation(self):
        """
        This method is needed to get a way to add a custom validation for
        the form.

        If you want add custom error to form you need to add FormError
        to self.form_errors in this method.

        >>> def validation(self) -> bool:
        >>>     if self.first_name or self.last_name:
        >>>         self.form_errors.append(
        >>>             FormError(
        >>>                 message='One of two field is required',
        >>>                 code=2,
        >>>             )
        >>>         )
        """
        pass

    class Meta:
        """
        For separate common settings and settings which connected with fields,
        all common setting should be defined in the Meta class.
        """
        method = 'POST'
        template = BASE_FORM_TEMPALTE
