import typing as t


__all__ = ['ConnectionInjector', ]


class ConnectionInjector:
    """
    This class need for share engines connection for admin's controllers. In
    aiohttp you initialize connection after start application and can't
    explicitly add it to controller class.

    create injector

    >>> postgres_connection = ConnectionInjector()

    provide connection in place where you initialize it

    >>> postgres_connection.init(db)

    inject connection to controller

    >>> @postgres_connection.inject
    >>> class Controller(PostgresController): pass
    """

    connection: t.Any

    def init(self, connection: t.Any) -> None:
        """
        This method need to specify connection which need to share.
        """
        self.connection = connection

    def inject(self, cls: object) -> object:
        """
        This method need to use as decorator for the controller class. It
        inject itself to decorated class as `connection_injector`.
        """
        cls.connection_injector = self
        return cls
