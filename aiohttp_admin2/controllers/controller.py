import logging
import typing as t
from collections import defaultdict

from aiohttp_admin2.resources.types import (
    PK,
    Instance,
    FiltersType,
)
from aiohttp_admin2.resources.abc import AbstractResource
from aiohttp_admin2.controllers.exceptions import PermissionDenied
from aiohttp_admin2.mappers import Mapper

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.controllers.types import (
    Cell,
    ListObject,
)

if t.TYPE_CHECKING:
    from aiohttp_admin2.controllers.relations import (
        ToManyRelation,
        ToOneRelation,
    )


logger = logging.getLogger(__name__)

# todo: test

# todo: move to url type
DETAIL_NAME = 'detail'
FOREIGNKEY_DETAIL_NAME = 'foreignkey_detail'


class Controller:
    """
    This class combine all business logic for work with instance.

        - CRUD
        - access
        - hooks
    """
    resource: AbstractResource
    mapper: Mapper = None
    name: str

    read_only_fields = []
    inline_fields = ['id', ]
    search_fields: t.List[str] = []
    # todo: handle list of fields
    fields: t.Union[str, t.Tuple[t.Any]] = '__all__'
    relations_to_one: t.List["ToOneRelation"] = []
    foreign_keys_map: t.Dict[str, "ToOneRelation"] = {}
    many_to_many = {}

    # CRUD access
    can_create = True
    can_update = True
    can_delete = True
    can_view = True

    # settings
    order_by = 'id'
    per_page = 50
    list_filter = []

    def __init__(self):
        self.prefetch_cache = defaultdict(dict)
        foreign_keys = [key for key in self.relations_to_one if not key.hidden]
        self.foreign_keys_map = {
            key.name: key
            for key in self.relations_to_one
        }
        for relation_to_one in foreign_keys:
            name = f'{relation_to_one.field_name}_field'

            async def _get_foreign(obj: Instance) -> t.Any:
                return await obj.get_relation(relation_to_one.name)

            _get_foreign.is_foreignkey = True

            if not hasattr(self, name):
                setattr(
                    self,
                    f'{relation_to_one.field_name}_field',
                    _get_foreign,
                )

    def get_resource(self):
        return self.resource

    # CRUD hooks
    async def pre_create(self, data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        This hook will be call before create an instance and give simple
        approach to do some before object will be created.

        :param data: data which will use for create an instance
        """
        return data

    async def pre_delete(self, pk: PK) -> None:
        """
        This hook will be call before delete an instance and give simple
        approach to do some before object will be deleted.

        :param pk: of instance which will delete
        """
        pass

    async def pre_update(self, data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        This hook will be call before update an instance and give simple
        approach to do some before object will be updated.

        :param data: data which will use for update an instance
        """
        return data

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

    async def update(
        self,
        pk: PK,
        data: t.Dict[str, t.Any],
    ) -> t.Union[Instance, Mapper]:
        await self.access_hook()

        if not self.can_update:
            raise PermissionDenied

        # todo: get_pk_name
        data['id'] = pk

        data = await self.pre_update(data)

        mapper = self.mapper(data)

        if mapper.is_valid():
            serialize_data = mapper.data
            del serialize_data['id']
            instance = Instance()
            instance.__dict__ = serialize_data

            instance = await self.get_resource().update(pk, instance)
            await self.post_update(instance)

            return instance

        return mapper

    async def create(
        self,
        data: t.Dict[str, t.Any],
    ) -> t.Union[Instance, Mapper]:
        await self.access_hook()

        if not self.can_create:
            raise PermissionDenied

        data = await self.pre_create(data)

        data['id'] = -1

        mapper = self.mapper(data)

        if mapper.is_valid():
            serialize_data = mapper.data
            del serialize_data['id']
            instance = Instance()
            instance.__dict__ = serialize_data

            instance = await self.get_resource().create(instance)

            await self.post_create(instance)

            return instance

        return mapper

    async def get_detail(self, pk: PK):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        data = await self.get_resource().get_one(pk)

        self.prepare_instances([data])

        return data

    def prepare_instances(self, instances: t.List[Instance]):
        controller_maps = {}

        # relations to one
        for foreignkey_name, foreignkey in self.foreign_keys_map.items():
            controller_maps[foreignkey_name] = foreignkey.controller()

        def _get_relation(instance: Instance):
            async def get_relation(name: str) -> Instance:
                controller = controller_maps.get(name)
                foreign_key = self.foreign_keys_map.get(name)
                cache = self.prefetch_cache.get(foreign_key.name)
                relation_id = getattr(instance, foreign_key.field_name)

                if cache:
                    if relation_id in cache.keys():
                        logger.debug(
                            f"Get data from cache {foreign_key.field_name} "
                            f"{relation_id}"
                        )
                        return cache.get(relation_id)

                fetch_ids = [
                    getattr(p, foreign_key.field_name)
                    for p in instance.prefetch_together
                ]

                data = await controller.get_many(
                    fetch_ids,
                    field=foreign_key.target_field_name,
                )

                logger.debug(
                    f"Fetch data {foreign_key.field_name} for {fetch_ids}"
                )

                self.prefetch_cache[foreign_key.name].update(data)

                return self.prefetch_cache[foreign_key.name].get(relation_id)

            return get_relation

        for i in instances:
            i.get_relation = _get_relation(i)

    async def get_list(
        self,
        url_builder,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
    ):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        list_data = await self.get_resource().get_list(
            page=page,
            cursor=cursor,
            limit=self.per_page,
            order_by=order_by or self.order_by,
            filters=filters,
        )

        self.prepare_instances(list_data.instances)

        rows = []

        for i in list_data.instances:
            row = []

            for index, field in enumerate(self.inline_fields):
                field_method_name = "{}_field".format(field)
                is_foreignkey = False
                is_safe = False

                if hasattr(self, field_method_name):
                    getter = getattr(self, field_method_name)
                    is_safe = \
                        hasattr(getter, 'is_safe')\
                        and getattr(getter, 'is_safe')
                    value = await getter(i)
                    if getattr(getter, 'is_foreignkey', False):
                        is_foreignkey = True
                else:
                    value = getattr(i, field)

                if index == 0 and self.can_update:
                    # todo: can view
                    url = url_builder(i, DETAIL_NAME)
                elif is_foreignkey:
                    # todo: can view, can edit
                    url = url_builder(
                        value,
                        FOREIGNKEY_DETAIL_NAME,
                        # todo: drop detail prefix
                        # relation to one
                        url_name=self.foreign_keys_map.get(field)
                            .controller()
                            .url_name()
                    )
                else:
                    url = None

                row.append(Cell(value=value, is_safe=is_safe, url=url))

            rows.append(row)

        return ListObject(
            rows=rows,
            has_next=list_data.has_next,
            hex_prev=list_data.hex_prev,
            count=list_data.count,
            active_page=list_data.active_page,
            per_page=list_data.per_page,
        )

    async def get_many(self, pks: t.List[PK], field: str = None):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        return await self.get_resource().get_many(pks, field=field)

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

    @classmethod
    def url_name(cls) -> str:
        return "_".join(cls.name.lower().split(" "))
