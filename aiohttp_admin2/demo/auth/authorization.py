from aiohttp_security import AbstractAuthorizationPolicy

from .users import user_map


class AuthorizationPolicy(AbstractAuthorizationPolicy):
    """
    This class implement access policy to admin interface.
    """

    async def permits(self, identity, permission, context=None) -> bool:
        user = user_map.get(identity)

        if permission in user.permission:
            return True

        return False

    async def authorized_userid(self, identity) -> int:
        return identity
