"""
In this test file we testing all workflow with a form that was
initialized without data. A form that was initialized without
data use only for one target for render html.
"""

from aiohttp_admin2.core.forms import BaseForm
from aiohttp_admin2.core import fields
from aiohttp import web
from aiohttp_admin2.core.constants import REQUIRED_MESSAGE_ERROR


async def test_default_fields(app):
    """
    All fields have a default value, but user can possible change this
    value. In this test we check correct work for native default value
    and default value that user changed.

        1. check a default value of TextField in a form's object
        2. check a custom value of TextField in a form's object

        3. check a default value of TextField in a render form
        4. check a custom value of TextField in a render form

        5. check a correct input name
    """

    class TestForm(BaseForm):
        text_field = fields.TextField()
        text_field_with_default = fields.TextField(
            default='default text',
        )

    test_form = TestForm()

    # 1. check a default value of TextField in a form's object
    assert test_form['text_field'] == ''

    # 2. check a custom value of TextField in a form's object
    assert test_form['text_field_with_default'] == 'default text'

    html = test_form.render_to_html()

    # 3. check a default value of TextField in a render form
    assert 'value=""' in html

    # 4. check a custom value of TextField in a render form
    assert 'value="default text"' in html

    # 5. check a correct input name
    assert 'name="text_field"' in html
    assert 'name="text_field_with_default"' in html


def test_required_fields():
    """
    Required fields can't be empty, so if we check valid of form we
    should get errors.

        1. check that form with empty required field is invalid
           (existing errors in render)
        2. check that form with required field wich has no empty
           default value is valid
        3. check required attribute in render form that has
           required field
    """
    class TestForm(BaseForm):
        required_text_field = fields.TextField(required=True)
    
    test_form = TestForm()

    # 1. check that form with empty required field is invalid (existing
    #  errors in render)
    assert not test_form.is_valid()
    html = test_form.render_to_html()

    assert REQUIRED_MESSAGE_ERROR in html

    # 2. check that form with required field wich has no empty default
    # value is valid
    class NewTestForm(BaseForm):
        required_text_field_with_default = fields.TextField(
            default='default text',
            required=True,
        )
    
    new_test_form = NewTestForm()

    assert new_test_form.is_valid()

    # 3. check required attribute in render form that has required field
    assert 'required="required"' in html


def test_correct_render_form():
    """
    In this test we check a correct render for form.

        1. check if existing a submit button
        2. check a form method
        3. check correct name of inputs
        4. check redefine a method
        5. check redefine a template
    """
    class TestForm(BaseForm):
        text_field = fields.TextField()
        text_field_with_default = fields.TextField(
            default='default text',
        )

    test_form = TestForm()
    html = test_form.render_to_html()


    # 1. check if existing a submit button
    assert 'type="submit"' in html

    # 2. check a form method
    assert 'method="POST"' in html

    # 3. check correct name of inputs
    assert 'name="text_field"' in html
    assert 'name="text_field_with_default"' in html

    # 4. check redefine a method
    class NewTestForm(BaseForm):
        class Meta:
            method = 'GET'
            template = 'new template method="{method}"'
    
    new_test_form = NewTestForm()
    html = new_test_form.render_to_html()

    assert 'method="GET"' in html

    # 5. check redefine a template
    assert 'new template' in html
