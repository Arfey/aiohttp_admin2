from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


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


def test_choice_generation():
    """
    In this test we check correct generation a choices property for the
    ChoicesField field.
    """
    assert ChoiceMapper({}).fields['type'].choices == gender_choices


def test_correct_validation():
    """
    In this test we check that mapper will valid only if ChoicesField's value
    contain in choices list
    """
    assert not ChoiceMapper({"type": "bad value"}).is_valid()
    assert ChoiceMapper({"type": "female"}).is_valid()


def test_correct_for_default_field():
    """
    In this test we check that mapper will set default value to the
    ChoicesField if value is not specify.
    """
    mapper = ChoiceMapper({})
    assert mapper.is_valid()
    assert mapper.data['type'] == 'male'


def test_bad_default_value():
    """
    If `default` value is not in choices that mapper must be is not valid.
    """

    class InnerMapper(Mapper):
        type = fields.ChoicesField(
            field_cls=fields.StringField,
            choices=gender_choices,
            default='wrong'
        )

    mapper = InnerMapper({})
    assert not mapper.is_valid()
