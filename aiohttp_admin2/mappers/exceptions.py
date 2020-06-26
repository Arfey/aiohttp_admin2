from aiohttp_admin2.exceptions import AdminException


__all__ = ['ValidationError', ]


class ValidationError(AdminException):
    """This exception connected with wrong mapper form or some field."""
