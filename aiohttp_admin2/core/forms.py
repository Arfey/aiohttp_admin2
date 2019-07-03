from aiohttp_admin2.core.fields.abc import FieldABC


class FormMeta(type):
    """
    Metaclass for all admin forms.
    """
    def __new__(mcs, name, bases, attrs):
        attrs = mcs._get_not_fields_attrs(attrs)
        new_class = super().__new__(mcs, name, bases, attrs)

        fields = {}

        for class_obj in reversed(new_class.__mro__):
            if hasattr(class_obj, '_fields'):
                fields.update(class_obj._fields)

        new_class._fields = fields

        return new_class

    @staticmethod
    def _get_not_fields_attrs(attrs):
        return dict(
            filter(
                lambda field: not isinstance(field[1], FieldABC),
                attrs.items()
            )
        )


class BaseForm(metaclass=FormMeta):
    """
    The base class for all admin forms.
    """
    def __init__(self, *args, **kwargs):
        pass

    def get_html(self, instance=None):
        """
        This method generate html code for create / edit form in admin
        interface. If instance is not empty form will be with predefine inputs.
        """
        pass

    def is_valid(self) -> bool:
        """
        This method provide validation for form and must be call before save.
        """
        pass

    def save(self):
        """
        If form is valid then form will create / update instance in data store.
        """
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}()'
