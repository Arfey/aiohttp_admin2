class Widget:
    """
    This class provide default behaviour of admin's widget. A widget is object
    that define view of field in html and all other stuff witch need for render
    a field.
    """
    def get_html(self):
        return 'text'
