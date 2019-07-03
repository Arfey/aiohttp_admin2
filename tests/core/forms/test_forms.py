from aiohttp_admin2.core.forms import BaseForm
from aiohttp_admin2.core import fields


# def test_init_base_form_wihtout_data():
#     """
#     In this test we check simple initialization and usage of from
#     without data. Form without data use only for one target for
#     render html.

#         1. Initialize a form without data
#         2. Render html for current form
#     """
#     class MyForm(BaseForm):
#         pass

#     my_from = MyForm()



def test_create_simple_form():
    """
    docs
    """
    class TestFrom(BaseForm):
        text_field = fields.TextField('text_field')

    my_form = TestFrom()


    class NewForm(TestFrom):
        pass
        # text2_field = fields.TextField('text2_field')

    next_form = TestFrom()

    class NewForm2(NewForm):
        text_field = fields.TextField('text_field')
        a = 1

    next2_form = NewForm2()

    print(next2_form.__class__.__mro__)
    print(next2_form.a)

    # assert len(next_form._fields) == 2

