__all__ = [
    'BaseWidget',
    'StringWidget',
    'LongStringWidget',
    'ChoiceWidget',
    'BooleanWidget',
    'ArrayWidget',
    'CKEditorWidget',
    'DateTimeWidget',
    'DateWidget',
    'FileWidget',
    'ImageWidget',
]


JQUERY_CDN = "https://code.jquery.com/jquery-3.5.1.min.js"


class BaseWidget:
    css_extra = []
    js_extra = []


class StringWidget(BaseWidget):
    """This widget represent a field as a simple text input."""
    template_name = 'aiohttp_admin/blocks/form/fields/string_field.html'


class LongStringWidget(BaseWidget):
    """This widget represent a field as a simple text input."""
    template_name = 'aiohttp_admin/blocks/form/fields/long_string_field.html'


class ChoiceWidget(BaseWidget):
    """This widget represent a field as a select input."""
    template_name = 'aiohttp_admin/blocks/form/fields/choice_field.html'


class BooleanWidget(BaseWidget):
    """This widget represent a field as a checkbox input."""
    template_name = 'aiohttp_admin/blocks/form/fields/boolean_field.html'


class ArrayWidget(BaseWidget):
    """This widget represent a field as a list of the separated tags."""
    template_name = 'aiohttp_admin/blocks/form/fields/array_field.html'
    js_extra = [
        JQUERY_CDN,
        (
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/"
            "bootstrap-tagsinput.min.js"
        ),
    ]


class CKEditorWidget(BaseWidget):
    """This widget represent a field as a smart html editor."""
    template_name = 'aiohttp_admin/blocks/form/fields/ck_editor_field.html'
    js_extra = [
        "https://cdn.ckeditor.com/4.15.0/standard/ckeditor.js"
    ]


class DateTimeWidget(BaseWidget):
    """This widget represent a field as a input with the datetime dropdown."""
    template_name = 'aiohttp_admin/blocks/form/fields/datetime_field.html'
    js_extra = [
        JQUERY_CDN,
        (
            "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/"
            "moment.min.js"
        ),
        (
            "https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/"
            "5.0.1/js/tempusdominus-bootstrap-4.min.js"
        )

    ]
    css_extra = [
        (
            "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap."
            "min.css"
        ),
        (
            "https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/"
            "5.0.1/css/tempusdominus-bootstrap-4.min.css"
        ),
    ]


class DateWidget(DateTimeWidget):
    """This widget represent a field as a input with the date dropdown."""
    template_name = 'aiohttp_admin/blocks/form/fields/date_field.html'


class JsonWidget(BaseWidget):
    """This widget represent a field as a smart json editor."""
    template_name = 'aiohttp_admin/blocks/form/fields/json_field.html'
    js_extra = [
        "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js",
    ]


class FileWidget(BaseWidget):
    """This widget represent a field as a file input."""
    template_name = 'aiohttp_admin/blocks/form/fields/file_field.html'


class ImageWidget(BaseWidget):
    """
    This widget represent a field as a file input with an image
    representation.
    """
    template_name = 'aiohttp_admin/blocks/form/fields/image_field.html'


class AutocompleteStringWidget(StringWidget):
    """
    This widget represent a field as a text input with able to suggests.
    """
    template_name = 'aiohttp_admin/blocks/form/fields/autocomplete_field.html'
    css_extra = [
        (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2."
            "min.css"
        ),
    ]
    js_extra = [
        JQUERY_CDN,
        (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2."
            "min.js"
        ),
    ]
