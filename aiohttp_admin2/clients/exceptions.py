from aiohttp_admin2.exceptions import AdminException


__all__ = ['ClientException', 'InstanceDoesNotExist', ]


class ClientException(AdminException):
    """The main exception for client exceptions."""


class InstanceDoesNotExist(ClientException):
    """Client can't return instance because it does not exists."""
