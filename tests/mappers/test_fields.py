from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


def test_choices_field():
    """
     In this test we check correct ChoicesField:

        1. correct generate choices
        2. correct validation
        3. work of `default` parameter
    """

    gender_choices = (
        ('male', "male"),
        ('female', "female"),
    )

    class ChoiceMapper(Mapper):
        type = fields.ChoicesField(
            field_cls=fields.StringField,
            choices=gender_choices,
            default='male'
        )

    # 1. correct generate choices
    assert ChoiceMapper({}).fields['type'].choices == gender_choices

    # 2. correct validation
    assert not ChoiceMapper({"type": "bad value"}).is_valid()
    assert ChoiceMapper({"type": "female"}).is_valid()

    #  3. work of `default` parameter
    assert ChoiceMapper({}).is_valid()


