__all__ = [
    'BaseWidget',
    'StringWidget',
    'ChoiceWidget',
    'BooleanWidget',
    'ArrayWidget',
    'CKEditorWidget',
]


class BaseWidget:
    css_extra = []
    js_extra = []


class BaseWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/string_field.html'


class StringWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/string_field.html'


class ChoiceWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/choice_field.html'


class BooleanWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/boolean_field.html'


class ArrayWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/array_field.html'
    js_extra = [
        "https://code.jquery.com/jquery-3.5.1.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/bootstrap-tagsinput.min.js",
    ]
    css_extra = [
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/bootstrap-tagsinput.css",
        "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
    ]


class CKEditorWidget(BaseWidget):
    template_name = 'aiohttp_admin/fields/ck_editor_field.html'
    js_extra = [
        "https://cdn.ckeditor.com/4.15.0/standard/ckeditor.js"
    ]

# class JsonWidget(BaseWidget):
#     template_name = 'aiohttp_admin/fields/json_field.html'
#     js_extra = [
#         "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.1.0/jsoneditor-minimalist.min.js",
#     ]
#     css_extra = [
#         "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.1.0/jsoneditor.min.css"
#     ]
# https://codepen.io/cahil/pen/qYpbGL
