from aiohttp_admin2.managers.postgres_manager.postgres_manager import \
    PostgresManager
from aiohttp_admin2.managers.abc import Instance
from aiohttp_admin2.managers.types import PK


__all__ = ['MySqlManager', ]


class MySqlManager(PostgresManager):

    async def create(self, instance: Instance) -> Instance:
        data = instance.__dict__
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

            return self.row_to_instance(data)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        data = instance.__dict__
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

            return self.row_to_instance(data)
