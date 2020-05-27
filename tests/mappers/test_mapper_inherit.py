from aiohttp_admin2.mappers import (
    Mapper,
    fields,
)


def test_mapper_inherit():
    """
    In this test we check correct work of combining fields by inherit base
    classes.

        1. Test combine difference fields
        2. Test rewrite existing fields
    """
    # 1. Test combine difference fields
    class BaseMapper(Mapper):
        base_field = fields.StringField()

    class ChildClass(BaseMapper):
        child_field = fields.IntField()

    mapping = ChildClass({
        "base_field": "value1",
        "child_field": 2
    })

    assert len(mapping.fields) == 2

    assert isinstance(mapping.fields["base_field"], fields.StringField), \
        "base_field must be StringField type"

    assert isinstance(mapping.fields["child_field"], fields.IntField), \
        "child_field must be IntField type"

    # 2. Test rewrite existing fields
    class SecondChildClass(ChildClass):
        child_field = fields.StringField()

    mapping = SecondChildClass({
        "base_field": "value1",
        "child_field": "value2"
    })

    assert len(mapping.fields) == 2

    assert isinstance(mapping.fields["base_field"], fields.StringField), \
        "base_field must be StringField type"

    assert isinstance(mapping.fields["child_field"], fields.StringField), \
        "child_field must be StringField type"
