import typing as t
from abc import (
    ABC,
    abstractmethod,
)

from aiohttp_admin2.mappers.exceptions import ValidationError

__all__ = ['AbstractField', ]


class EmptyValue:
    def __repr__(self):
        return ''

# todo: add validators


class AbstractField(ABC):
    def __init__(
        self,
        required: bool = False,
        validators: t.List[t.Any] = [],
        value: t.Any = None,
    ) -> None:
        self.name: str = None
        self._value: t.Any = value
        self.errors: t.List[t.Optional[str]] = []
        self.required = required
        self.validators = validators

    @abstractmethod
    def to_python(self) -> t.Any:
        """
        Convert value to correct python type equivalent.

        Raises:
            ValueError: if type of value is wrong
        """
        pass

    @abstractmethod
    def to_raw(self) -> t.Any:
        """
        Convert value to correct storage type.

        Raises:
            ValueError: if type of value is wrong
        """
        pass

    @property
    def value(self):
        """
        Convert value to correct python type equivalent.

        Raises:
            ValueError: if type of value is wrong
        """
        return self.to_python()

    @property
    def raw_value(self):
        return self.to_raw()

    def is_valid(self) -> bool:
        """
        In this method check is current field valid and have correct value.

        Raises:
            ValidationError: if failed validators
            ValueError, TypeError: if type of value is wrong

        """
        if self.required and not self.value:
            raise ValidationError(F"{self.name} field is required.")
        self.to_python()
        self.to_raw()

        return True

    def __call__(self, value: t.Any) -> "AbstractField":
        return self.__class__(
            required=self.required,
            validators=self.validators,
            value=value
        )

    def __repr__(self):
        return \
            f"{self.__class__.__name__}(name={self.name}, value={self._value})"
