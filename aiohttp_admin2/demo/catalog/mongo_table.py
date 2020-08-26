from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance as MInstance, Document, fields, validate


class TestTable(Document):
    name = fields.StringField(required=True, unique=True)
    age = fields.IntegerField()

    class Meta:
        collection_name = "test_mongo"
