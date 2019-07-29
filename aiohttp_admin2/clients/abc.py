from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Optional,
    List,
    Any,
    Dict,
    Tuple,
)

__all__ = ['ABCClient', ]


CommonErrorsType = Dict[str, str]


class ABCClient(ABC):
    """
    docs
    """
    @abstractmethod
    def get_object_by_id(self, pk: Optional[int, str]) -> Any:
        """
        docs
        """

    @abstractmethod
    def get_list(self, *, page: int = 1, per: int = 50) -> List[Any]:
        """
        docs
        """

    @abstractmethod
    def create_or_update(self, data: Dict[Any, Any]) -> Tuple[bool, CommonErrorsType]:
        """
        docs
        """

    @abstractmethod
    def delete_object_by_id(self, pk: int) -> Tuple[bool, CommonErrorsType]:
        """
        In this method you should implement logic for delete instance with
        given `id`. This method must return tuple where first argument it's
        optional deleted instance and second it's optional list of errors.
        """
