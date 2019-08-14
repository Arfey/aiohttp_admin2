"""
The one of main pages in an admin interface is listing. In this test
file we check a base features of it.
"""

# TODO: test name of field 

def test_simple_listing_wthout_any_settings():
    """
    By default, a listing has some features:

        1. page has a paggination
        2. list of instances with one field
        3. first field is a link to detail page
        4. first field has sort button
    """
    pass


def test_custom_fields():
    """
    User has possible to add to listing some custom field.

        1. add simple custom field
        2. a custom field doesn't have a sort button
        3. a custom field must be a read only field
    """
    pass


def test_access_hook():
    """
    The all access rules for all pages in admin interface, you should
    provide in access_hook method and listing is not a exception.
    
    You can setting:

        1. a list of visibilited fields
        2. hidde a create button (can_create)
        3. hide possibility to edit (can_update)
    """
    pass
