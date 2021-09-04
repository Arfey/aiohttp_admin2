import typing as t
from abc import ABC
from abc import abstractmethod

from aiohttp_admin2.mappers.validators import required as required_validator
from aiohttp_admin2.mappers.validators import length

__all__ = ['AbstractField', ]


class AbstractField(ABC):
    type_name: str = 'string'

    def __init__(
        self,
        *,
        required: bool = False,
        validators: t.List[t.Callable[[t.Any], None]] = None,
        value: t.Optional[str] = None,
        default: t.Optional[t.Any] = None,
        primary_key: bool = False,
        **kwargs: t.Any,
    ) -> None:
        self.default: t.Optional[str] = default
        self._value: t.Optional[str] = value
        self.errors: t.List[t.Optional[str]] = []
        self.required = required
        self.validators = validators or []
        self.kwargs = kwargs
        self.primary_key = primary_key
        self.init_default_validators()

    def init_default_validators(self):
        if self.required:
            self.validators.append(required_validator)

        max_length = self.kwargs.get('max_length')

        if max_length:
            self.validators.append(length(max_value=max_length))

    @abstractmethod
    def to_python(self) -> t.Any:
        """
        Convert value to correct python type equivalent.

        Raises:
            ValueError: if type of value is wrong
        """
        pass

    def to_storage(self) -> str:
        """
        Convert value to correct storage type.
        """
        return str(self._value) if self._value is not None else ''

    @property
    def value(self) -> t.Any:
        """
        Convert value to correct python type equivalent.

        Raises:
            ValueError: if type of value is wrong
        """
        return self.to_python()

    def apply_default_if_need(self) -> None:
        if self._value is None and self.default:
            self._value = self.default

    @property
    def raw_value(self) -> t.Any:
        return self.to_storage()

    @property
    def failure_safe_value(self) -> t.Any:
        """
        This method need to return value even if value is invalid. It's might
        be helpful in case when we need to show error and show value which
        raise current error.
        """
        try:
            return self.value
        except Exception:
            return self.raw_value

    @property
    def is_not_none(self):
        return self._value is not None

    def is_valid(self) -> bool:
        """
        In this method check is current field valid and have correct value.

        Raises:
            ValidationError: if failed validators
            ValueError, TypeError: if type of value is wrong

        """
        self.to_python()
        self.to_storage()

        for validator in self.validators:
            validator(self.value)

        return True

    def __call__(self, value: t.Any) -> "AbstractField":
        return self.__class__(
            required=self.required,
            validators=self.validators,
            default=self.default,
            primary_key=self.primary_key,
            value=value
        )

    def __repr__(self):
        return \
            f"{self.__class__.__name__}(name={self.type_name}," \
            f" value={self._value}), required={self.required}" \
            f" primary_key={self.primary_key})"
