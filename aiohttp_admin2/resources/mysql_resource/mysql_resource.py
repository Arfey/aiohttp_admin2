from aiohttp_admin2.resources.postgres_resource.postgres_resource import \
    PostgresResource
from aiohttp_admin2.resources.abc import Instance
from aiohttp_admin2.resources.types import PK


__all__ = ['MySqlResource', ]


class MySqlResource(PostgresResource):

    async def create(self, instance: Instance) -> Instance:
        data = instance.data
        async with self.engine.acquire() as conn:
            query = self.table\
                .insert()\
                .values([data])

            result = await conn.execute(query)

            query = self.table\
                .select()\
                .where(self._primary_key == result.lastrowid)

            cursor = await conn.execute(query)
            data = await cursor.fetchone()

            await conn.execute('commit;')

            return self._row_to_instance(data)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        data = instance.data
        async with self.engine.acquire() as conn:
            query = self.table\
                .update()\
                .where(self._primary_key == pk)\
                .values(**data)

            await conn.execute(query)

            query = self.table\
                .select()\
                .where(self._primary_key == pk)

            cursor = await conn.execute(query)
            data = await cursor.fetchone()

            await conn.execute('commit;')

            return self._row_to_instance(data)
