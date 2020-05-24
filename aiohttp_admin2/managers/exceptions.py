from aiohttp_admin2.exceptions import AdminException


__all__ = [
    'ClientException',
    'InstanceDoesNotExist',
    'FilterException',
    'BadParameters',
    'CURSOR_PAGINATION_ERROR_MESSAGE',
]


CURSOR_PAGINATION_ERROR_MESSAGE = \
    "Pagination by cursor available only together with sorting by primary key"


class ClientException(AdminException):
    """The main exception for client exceptions."""


class InstanceDoesNotExist(ClientException):
    """Manager can't return instance because it does not exists."""


class FilterException(ClientException):
    """Manager can't apply filter to query."""


class BadParameters(AdminException):
    """Bad arguments for method."""
