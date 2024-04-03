from sqlalchemy.dialects import mysql

from aiohttp_admin2.resources.postgres_resource.postgres_resource import \
    PostgresResource
from aiohttp_admin2.resources.abc import Instance
from aiohttp_admin2.resources.types import PK

try:
    from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql
    # waiting for fix https://github.com/aio-libs/aiomysql/discussions/908
    MySQLDialect_pymysql.case_sensitive = True
except ImportError:
    raise ImportError('aiomysql.sa requires sqlalchemy')


__all__ = ['MySqlResource', ]


class MySqlResource(PostgresResource):

    _dialect = mysql.dialect()

    async def _execute(self, conn, query):
        if not isinstance(query, str):
            # fixed problem with post compile in aio-mysql
            query = str(
                query.compile(
                    compile_kwargs={"literal_binds": True},
                    dialect=self._dialect,
                )
            )

        return await conn.execute(query)

    async def create(self, instance: Instance) -> Instance:
        data = instance.data.to_dict()
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
        data = instance.data.to_dict()
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
