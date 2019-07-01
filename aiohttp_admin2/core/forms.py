from .fields.abc import FieldABC


class FormMeta(type):
    """
    Metaclass for all admin forms.
    """
    def __new__(cls, name, bases, properties):
        # default
        # empty fields

        properties = cls._separate_fields(properties)

        return cls.__new__(name, bases, properties)

    @staticmethod
    def _separate_fields(data):
        """
        Separate simple property
        """

        fields = []
        new_data = {}

        for key, obj_property in data.items():
            if isinstance(obj_property, FieldABC):
                fields.append(obj_property)
            else:
                new_data.update({key: obj_property})

        new_data['field'] = fields

        return new_data


class BaseForm(metaclass=FormMeta):
    """
    The base class for all admin forms.
    """
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


class Book(BaseForm):
    """

    """
    name = ''
