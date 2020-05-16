from abc import (
    ABC,
    abstractmethod,
)

import sqlalchemy as sa

from aiohttp_admin2.clients.exceptions import FilterException


__all__ = ["ABCFilter", ]


class ABCFilter(ABC):
    """

    """
    field_name: str
    value: str
    name: str

    @abstractmethod
    def apply(self) -> sa.sql.Select:
        """

        """
        pass

    def validate(self):
        """

        """
        pass

    @property
    def query(self) -> sa.sql.Select:
        """

        """
        try:
            self.validate()
        except Exception as e:
            msg = ""

            if e.args and isinstance(e.args[0], str):
                msg = e.args[0]

            raise FilterException(msg)

        return self.apply()
