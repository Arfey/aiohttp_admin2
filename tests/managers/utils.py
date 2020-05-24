import typing as t
from aiohttp_admin2.managers import Instance


async def generate_fake_instance(manager, n: int = 1) -> t.List[Instance]:
    instances: t.List[Instance] = []

    for i in range(n):
        obj = Instance()
        obj.val = f'some - {i}'

        instances.append(await manager.create(obj))

    return instances
