"""
In this test file we check correct work a form with data.
"""

from aiohttp_admin2.core.forms import BaseForm
from aiohttp_admin2.core import fields


def test_initialize_form_with_data():
    """
    In this test we check initialize form with data.

        1. Correct initialize a from
        2. Correct initialize a form with default fields
    """
    # 1. Correct initialize a from
    class NewSimpleForm(BaseForm):
        test_field = fields.TextField()
    
    new_simple_form = NewSimpleForm({'test_field': 'test'})

    assert new_simple_form['test_field'] == 'test'

    # 2. Correct initialize a form with default fields
    class NewDefaultForm(BaseForm):
        test_field = fields.TextField()
        default_test_field = fields.TextField(default='default')
        newx_default_test_field = fields.TextField(default='default')

    new_default_form = NewDefaultForm({
        'test_field': 'test',
        'newx_default_test_field': 'next_test',
    })

    assert new_default_form['test_field'] == 'test'
    assert new_default_form['default_test_field'] == 'default'
    assert new_default_form['newx_default_test_field'] == 'next_test'
