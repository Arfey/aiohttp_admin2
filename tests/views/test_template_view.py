"""
The template view need to represented a some custom user data in an
admin interface. So in this test file we check all possible use cases
that arise when we working with it.
"""


def test_simple_template_view():
    """
    By default, the template view without a custom date have some
    properties:

        1. In aside bar there is a link to the template view.
        2. In main block there is a text with name of template view.
    """
    pass


def test_template_view_with_custom_content():
    """
    The main goal of the template view it's give a possible to add
    some custom data in an admin interface. U can do that using:

        1. Rewrite get_context method for add a new content.
    """
    pass
