from aiohttp_security import AbstractAuthorizationPolicy


class AuthorizationPolicy(AbstractAuthorizationPolicy):
    """
    This class implement access policy to admin interface.
    """

    def permits(self, identity, permission, context=None) -> bool:
        return True

    def authorized_userid(self, identity) -> int:
        return 1
