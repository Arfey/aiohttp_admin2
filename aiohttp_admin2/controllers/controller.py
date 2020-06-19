import typing as t

from aiohttp_admin2.resources.types import (
    PK,
    Instance,
    FiltersType,
)
from aiohttp_admin2.resources.abc import AbstractResource
from aiohttp_admin2.controllers.exceptions import PermissionDenied
from aiohttp_admin2.mappers import Mapper

from aiohttp_admin2.mappers.fields.abc import AbstractField

# todo: test


class Controller:
    """
    This class combine all business logic for work with instance.

        - CRUD
        - access
        - hooks
    """
    resource: AbstractResource
    mapper: Mapper = None

    read_only_fields = []
    inline_fields = ['id', ]
    # todo: handle list of fields
    fields: t.Union[str, t.Tuple[t.Any]] = '__all__'

    # CRUD access
    can_create = True
    can_update = True
    can_delete = True
    can_view = True

    # settings
    order_by = 'id'
    per_page = 50

    def get_resource(self):
        return self.resource

    # CRUD hooks
    async def pre_create(self, data: t.Dict[str, t.Any]) -> None:
        """
        This hook will be call before create an instance and give simple
        approach to do some before object will be created.

        :param data: data which will use for create an instance
        """
        pass

    async def pre_delete(self, pk: PK) -> None:
        """
        This hook will be call before delete an instance and give simple
        approach to do some before object will be deleted.

        :param pk: of instance which will delete
        """
        pass

    async def pre_update(self, data: t.Dict[str, t.Any]) -> None:
        """
        This hook will be call before update an instance and give simple
        approach to do some before object will be updated.

        :param data: data which will use for update an instance
        """
        pass

    async def post_create(self, instance: Instance) -> None:
        """
        This hook will be call after create an instance and give simple
        approach to do some after object was created.

        :param instance: created instance
        """
        pass

    async def post_delete(self, pk: PK) -> None:
        """
        This hook will be call after delete an instance and give simple
        approach to do some after object was deleted.

        :param pk: of instance which was deleted
        """
        pass

    async def post_update(self, instance: Instance) -> None:
        """
        This hook will be call after update an instance and give simple
        approach to do some after object was updated.

        :param instance: updated instance
        """
        pass

    # access hook
    async def access_hook(self) -> None:
        """
        This method need to redefine settings (like can_create, can_update and
        etc.) and will be call before each call to resources.
        """
        pass

    # CRUD
    async def delete(self, pk: PK):
        await self.access_hook()

        if not self.can_delete:
            raise PermissionDenied

        await self.pre_delete(pk)
        await self.get_resource().delete(pk)
        await self.post_delete(pk)

    async def update(self, pk: PK, data: t.Dict[str, t.Any]):
        await self.access_hook()

        if not self.can_update:
            raise PermissionDenied

        await self.pre_update(data)
        instance = Instance()
        instance.__dict__ = data
        res = await self.get_resource().update(pk, instance)
        await self.post_update(res)

    async def create(self, data: t.Dict[str, t.Any]):
        await self.access_hook()

        if not self.can_create:
            raise PermissionDenied

        # todo: think about errors
        await self.pre_create(data)
        instance = Instance()
        instance.__dict__ = data
        res = await self.get_resource().create(instance)

        await self.post_create(res)

        return res

    async def get_detail(self, pk: PK):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        return await self.get_resource().get_one(pk)

    async def get_list(
        self,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
    ):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        return await self.get_resource().get_list(
            page=page,
            cursor=cursor,
            limit=self.per_page,
            order_by=order_by or self.order_by,
            filters=filters,
        )

    async def get_many(self, pks: t.List[PK]):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        return self.get_resource().get_many(pks)

    @classmethod
    def builder_form_params(cls, params: t.Dict[str, t.Any]):
        # todo: add params
        return cls()

    @property
    def detail_fields(self) -> t.Dict[str, AbstractField]:
        # todo: add for dict
        fields = self.mapper({}).fields
        if self.fields == "__all__":
            return fields

        return {
            name: value
            for name, value in fields
            if name in self.fields
        }