import typing as t
import re

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.string_field import StringField


__all__ = [
    "UrlField",
    "UrlFileField",
    "UrlImageField",
]


class UrlField(StringField):
    """
    This class is wrapper on `StringField` that can validate correct url
    address.
    """
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


class UrlFileField(UrlField):
    """
    This class just need to change visual representation in admin interface of
    field which contains url to the file.
    """
    type_name: str = 'url_file'

    def to_python(self) -> t.Optional[str]:
        if self._value and not hasattr(self._value, 'file'):
            return str(self._value)

        return self._value


class UrlImageField(UrlField):
    """
    This class just need to change visual representation in admin interface of
    field which contains url to the image.
    """
    type_name: str = 'url_file_image'

    def to_python(self) -> t.Optional[str]:
        if self._value and not hasattr(self._value, 'file'):
            if self._value in ('None', 'on'):
                return None

            return str(self._value)

        return self._value
