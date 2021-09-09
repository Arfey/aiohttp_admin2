import typing as t
from aiohttp_admin2.resources import Instance


async def generate_fake_instance(resource, n: int = 1) -> t.List[Instance]:
    instances: t.List[Instance] = []

    for i in range(n):
        obj = Instance()
        obj.data = {"val": f'some - {i}'}

        instances.append(await resource.create(obj))

    return instances
