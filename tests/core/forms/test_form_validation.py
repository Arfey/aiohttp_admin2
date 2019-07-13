"""
In this test file we testing validation for form. You can provide two
level of validation. The common validators allocated into fields it's
a first level but you can add validation for whole form for check
relationship between field it's second level of validation.
"""
from aiohttp_admin2.core.forms import BaseForm
from aiohttp_admin2.core import fields
from aiohttp_admin2.core.constants import (
    REQUIRED_CODE_ERROR,
    REQUIRED_MESSAGE_ERROR,
)


def test_required_param():
    """
    All field have required parameter that add validation for field witch
    raise error if the value is empty.

        1. Raise error if value is empty and field has a required
        parameter
        2. Don't raise error if value is empty and field dosen't have a
        required parameter
        3. Don't raise error if value is empty and field has a required and
        default parameter
        4. Don't raise error if value isn't empty and field has a required
        parameter
    """
    # 1. Raise error if value is empty and field has a required
    # parameter
    class MyRequiredForm(BaseForm):
        name = fields.TextField(required=True)

    my_required_form = MyRequiredForm()

    assert not my_required_form.is_valid()
    assert my_required_form._fields['name'].errors[0].message == REQUIRED_MESSAGE_ERROR
    assert my_required_form._fields['name'].errors[0].code == REQUIRED_CODE_ERROR

    # 2. Don't raise error if value is empty and field dosen't have a
    # required parameter

    # my_new_form = MyRequiredForm({'name': 'text'})

    # assert my_new_form.is_valid()

    # 3. Don't raise error if value is empty and field has a required and
    # default parameter

    class MyDefaultForm(BaseForm):
        name = fields.TextField(required=True, default='text')

    my_default_form = MyDefaultForm()

    assert my_default_form.is_valid()

    # 4. Don't raise error if value isn't empty and field has a required
    # parameter

    class MySimpleForm(BaseForm):
        name = fields.TextField()

    my_simple_form = MySimpleForm()

    assert my_simple_form.is_valid(), my_simple_form._fields['name'].errors


def test_default_validator_for_form():
    """
    The each field has its own validation that connected with
    de-serialization a data.

        1. Simple field with correct value
        2. Custom field with correct value
        3. Custom field with not correct value
    """
    pass


def test_form_validator():
    """
    The form provide an approach for a validation relationship between
    field.

        1. Succes relationship
        2. Bad relationship
    """
    pass
