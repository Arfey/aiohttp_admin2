from aiohttp_admin2.mappers import fields
from aiohttp_admin2.mappers.generics import MongoMapperGeneric
from umongo import Document
from umongo import fields as mongo_fields


# def test_generic_for_umongo_table():
#     """
#     In this test we check corrected work of auto generator for mapper from
#     umongo table.

#         1. Generate corrected fields from table.
#         2. Mixing generated fields and custom.
#         3. Rewriting generated fields
#     """

#     from umongo.frameworks import MotorAsyncIOInstance

#     instance = MotorAsyncIOInstance()

#     @instance.register
#     class User(Document):
#         age = mongo_fields.IntegerField()
#         email = mongo_fields.EmailField(required=True, unique=True)

#     class UserMapper(MongoMapperGeneric, table=User):
#         pass

#     user = UserMapper({"age": 18, "email": "some@gmail.com"})

#     # 1. Generate corrected fields from table. (with id field)
#     assert len(user.fields) == 3

#     assert isinstance(user.fields["age"], fields.IntField)
#     assert isinstance(user.fields["email"], fields.StringField)

#     # 2. Mixing generated fields and custom.
#     class UserMapper(MongoMapperGeneric, table=User):
#         some_field = fields.IntField()

#     user = UserMapper({"age": 18, "email": "some@gmail.com"})

#     assert len(user.fields) == 4
#     assert isinstance(user.fields["email"], fields.StringField)
#     assert isinstance(user.fields["age"], fields.IntField)
#     assert isinstance(user.fields["some_field"], fields.IntField)

#     # 3. Rewriting generated fields
#     class UserMapper(MongoMapperGeneric, table=User):
#         id = fields.IntField()

#     user = UserMapper({"age": 18, "email": "some@gmail.com"})

#     assert len(user.fields) == 3
#     assert isinstance(user.fields["email"], fields.StringField)
#     assert isinstance(user.fields["age"], fields.IntField)
#     assert isinstance(user.fields["id"], fields.IntField)


# def test_generic_validation_for_umongo_table():
#     """
#     In this test we check corrected work of mapper and marshmallow validation.

#         1. Corrected work of marshmallow and generic validation together
#         2. Corrected work of marshmallow validation
#     """
#     instance = MotorAsyncIOInstance()

#     @instance.register
#     class User(Document):
#         age = mongo_fields.IntegerField(required=True)
#         email = mongo_fields.EmailField(required=True, unique=True)

#     class UserMapper(MongoMapperGeneric, table=User):
#         other_field = fields.StringField(required=True)

#     # 1. Corrected work of generic validation
#     user = UserMapper({"age": 18, "email": "some@gmail.com"})

#     assert not user.is_valid()
#     assert not user.fields['age'].errors
#     assert not user.fields['email'].errors
#     assert user.fields['other_field'].errors

#     user = UserMapper({
#         "age": 18,
#         "email": "some@gmail.com",
#         "other_field": "text",
#     })

#     assert user.is_valid()

#     assert not user.fields['age'].errors
#     assert not user.fields['email'].errors
#     assert not user.fields['other_field'].errors
#     assert not user.error

#     # 2. Corrected work of marshmallow validation
#     user = UserMapper({
#         "id": 1,
#         "email": "text",
#     })

#     assert not user.is_valid()
#     assert user.fields['age'].errors
#     assert user.fields['email'].errors
