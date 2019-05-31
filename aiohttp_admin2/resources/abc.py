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

__all__ = ['AbstractResource', ]


CommonErrorsType = Dict[str, str]


class AbstractResource(ABC):
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
    def create(self, data: Dict[Any, Any]) -> Tuple[bool, CommonErrorsType]:
        """
        docs
        """

    @abstractmethod
    def delete(self) -> Tuple[bool, CommonErrorsType]:
        """
        docs
        """
