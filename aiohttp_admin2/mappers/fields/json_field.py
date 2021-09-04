import json
import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["JsonField", ]


class JsonField(AbstractField):
    type_name: str = 'json'

    def to_python(self) -> t.Optional[t.Dict[str, t.Any]]:
        if self._value and self._value.strip():
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
