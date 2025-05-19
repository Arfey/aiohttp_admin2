import logging
from enum import Enum
import typing as t
from collections import defaultdict
from contextvars import ContextVar

from aiohttp_admin2.resources.types import PK
from aiohttp_admin2.resources.types import Instance
from aiohttp_admin2.resources.types import FiltersType
from aiohttp_admin2.resources.abc import AbstractResource
from aiohttp_admin2.controllers.exceptions import PermissionDenied
from aiohttp_admin2.mappers import Mapper

from aiohttp_admin2.views import filters
from aiohttp_admin2.controllers.types import Cell
from aiohttp_admin2.controllers.types import ListObject

if t.TYPE_CHECKING:
    from aiohttp_admin2.controllers.relations import ToManyRelation  # noqa
    from aiohttp_admin2.controllers.relations import ToOneRelation  # noqa


logger = logging.getLogger(__name__)

# todo: test

# todo: move to url type
DETAIL_NAME = 'detail'
FOREIGNKEY_DETAIL_NAME = 'foreignkey_detail'

ControllerMap = ContextVar[t.Dict[t.Type['Controller'], 'Controller']]
controllers_map: ControllerMap = ContextVar('controllers_map', default=None)


class Controller:
    """
    This class combine all business logic for work with instance.

        - CRUD
        - access
        - hooks
    """
    resource: AbstractResource
    mapper: t.Type[Mapper] = None
    name: str = ''

    read_only_fields = []
    inline_fields = ['id', ]
    search_fields: t.List[str] = []
    autocomplete_search_fields: t.List[str] = []
    # todo: handle list of fields
    fields: t.Union[str, t.Tuple[t.Any]] = '__all__'
    relations_to_one: t.List["ToOneRelation"] = []
    relations_to_many: t.List["ToManyRelation"] = []
    foreign_keys_map: t.Dict[str, "ToOneRelation"] = {}
    foreign_keys_field_map: t.Dict[str, "ToOneRelation"] = {}
    many_to_many = {}
    exclude_update_fields = ['id', ]
    exclude_create_fields = ['id', ]

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
        self.foreign_keys_field_map = {
            key.field_name: key
            for key in foreign_keys
        }
        # todo: relation list created a lot of instances
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

        # in some cases when user can update instance but don't have access to
        # all fields mapper will raise an error if inaccessible field is
        # required (or pk field is hidden), to avoid it we fetch instance from
        # db before that and merge with data which have been provided by user.
        db_instance = await self.get_resource().get_one(pk)
        data = {**db_instance.data.to_dict(), **data}

        data = await self.pre_update(data)

        mapper = self.mapper(data)

        if mapper.is_valid():
            serialize_data = mapper.data
            instance = Instance()

            if self.fields == '__all__':
                instance.data = serialize_data
            else:
                # in this place we skip update of field which not present in
                # fields list. This need for partial update of instance when
                # update page don't have full list of fields
                instance.data = {
                    key: value for key, value in serialize_data.items()
                    if key in self.fields
                }

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

        mapper = self.mapper(data)

        if mapper.is_valid(skip_primary=True):
            serialize_data = mapper.data
            instance = Instance()
            instance.data = serialize_data

            instance = await self.get_resource().create(instance)

            await self.post_create(instance)

            return instance

        return mapper

    async def get_detail(self, pk: PK):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        data = await self.get_resource().get_one(pk)

        await self.prepare_instances([data])

        return data

    async def prepare_instances(self, instances: t.List[Instance]):
        controller_maps = {}

        # relations to one
        for foreignkey_name, foreignkey in self.foreign_keys_map.items():
            controller_maps[foreignkey_name] = foreignkey.controller.builder()

        def _get_relation(instance: Instance):
            async def get_relation(name: str) -> Instance:
                controller = controller_maps.get(name)
                foreign_key = self.foreign_keys_map.get(name)
                cache = self.prefetch_cache.get(foreign_key.name)
                relation_id = getattr(instance.data, foreign_key.field_name)

                if cache:
                    if relation_id in cache.keys():
                        logger.debug(
                            f"Get data from cache {foreign_key.field_name} "
                            f"{relation_id}"
                        )
                        return cache.get(relation_id)

                fetch_ids = [
                    getattr(p.data, foreign_key.field_name)
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
            if i:
                i.get_relation = _get_relation(i)
                i.set_name(await self.get_object_name(i))

    async def get_autocomplete_items(self, *, text: str, page: int):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        search_fields = \
            self.autocomplete_search_fields or self.search_fields

        if not search_fields:
            return {}

        filters_list = [
            filters.FilterMultiTuple(
                search_fields,
                text,
                'search_multi',
            ),
        ]

        list_data = await self.get_resource().get_list(
            limit=self.per_page,
            order_by=self.order_by,
            filters=filters_list,
            page=page,
            with_count=True,
        )

        await self.prepare_instances(list_data.instances)

        return {
            "results": [
                {"id": i.get_pk(), "text": str(i)}
                for i in list_data.instances
            ],
            "pagination": {
                "more": list_data.has_next
            }
        }

    def is_field_sortable(self, name: str, use_infinity: bool) -> bool:
        field_method_name = "{}_field".format(name)
        sort_method_name = "{}_field_sort".format(name)

        has_sort_method = (
            not hasattr(self, field_method_name)
            or hasattr(self, sort_method_name)
        )

        if has_sort_method:
            if not use_infinity:
                return True
            elif name in ['id', 'pk']:
                return True

        return False

    async def get_list(
        self,
        url_builder,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
        with_count: bool = True,
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
            with_count=with_count,
        )

        await self.prepare_instances(list_data.instances)

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
                    value = getattr(i.data, field)

                    if isinstance(value, Enum):
                        value = value.value

                url = None

                if index == 0 and (self.can_update or self.can_view):
                    url = url_builder(i, DETAIL_NAME)
                elif is_foreignkey:
                    foreign_key_controller = self.foreign_keys_map.get(field)\
                        .controller.builder()
                    if (
                        (
                            foreign_key_controller.can_update or
                            foreign_key_controller.can_view
                        ) and value
                    ):
                        url = url_builder(
                            value,
                            FOREIGNKEY_DETAIL_NAME,
                            # todo: relation to one
                            url_name=foreign_key_controller.url_name()
                        )

                row.append(Cell(value=value, is_safe=is_safe, url=url))

            rows.append(row)

        return ListObject(
            rows=rows,
            has_next=list_data.has_next,
            has_prev=list_data.has_prev,
            count=list_data.count,
            active_page=list_data.active_page,
            per_page=list_data.per_page,
            next_id=list_data.next_id,
        )

    async def get_many(self, pks: t.List[PK], field: str = None):
        await self.access_hook()

        if not self.can_view:
            raise PermissionDenied

        data = await self.get_resource().get_many(pks, field=field)
        await self.prepare_instances(data.values())

        return data

    async def get_object_name(self, obj: Instance) -> str:
        return str(obj)

    @classmethod
    def with_autocomplete(cls):
        return bool(cls.autocomplete_search_fields or cls.search_fields)

    @classmethod
    def builder(cls):
        ctr_map = controllers_map.get() or {}
        controller = ctr_map.get(cls)

        if not controller:
            controller = cls()
            ctr_map[cls] = controller
            controllers_map.set(ctr_map)

        return controller

    @classmethod
    def url_name(cls) -> str:
        return "_".join(cls.get_name().split(" "))

    @classmethod
    def get_name(cls) -> str:
        return cls.name.lower() or cls.__name__.lower()
