from aiohttp_admin2.exceptions import AdminException


__all__ = [
    'ClientException',
    'InstanceDoesNotExist',
    'FilterException',
    'CURSOR_PAGINATION_ERROR_MESSAGE',
]


CURSOR_PAGINATION_ERROR_MESSAGE = \
    "Pagination by cursor available only together with sorting by primary key"


class ClientException(AdminException):
    """The main exception for client exceptions."""


class InstanceDoesNotExist(ClientException):
    """Client can't return instance because it does not exists."""


class FilterException(ClientException):
    """Client can't apply filter to query."""
