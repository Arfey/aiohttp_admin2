from aiohttp_admin2.exceptions import AdminException

__all__ = [
    'CanNotModifiedFrozenView',
    'CanNotCreateUnfrozenView',
    'NoUniqueController',
    'NotRegisterView',
    'NoUniqueControllerName',
    'UseHandlerWithoutAccess',
]


class CanNotModifiedFrozenView(AdminException):
    """We can't modified static properties in the frozen view."""


class CanNotCreateUnfrozenView(AdminException):
    """
    We can't instantiate the unfrozen view. U need setup the view before
    create.
    """


class NoUniqueController(AdminException):
    """Register views with common controller is forbidden."""


class NoUniqueControllerName(AdminException):
    """Register controller with common name is forbidden."""


class NotRegisterView(AdminException):
    """View is not register for admin interface"""


class UseHandlerWithoutAccess(AdminException):
    """You call handler without check access"""
