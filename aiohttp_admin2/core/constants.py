from typing import Union

from dataclasses import dataclass

__all__ = [
    'FormError',
    'UNKNOW_ERROR',
    'REQUIRED_MESSAGE_ERROR',
    'REQUIRED_CODE_ERROR',
]

# errors
UNKNOW_ERROR = 'UNKNOW_ERROR'

REQUIRED_MESSAGE_ERROR = 'field is required'
REQUIRED_CODE_ERROR = 1

EMAIL_MESSAGE_ERROR = 'email is not valid'
EMAIL_CODE_ERROR = 2


@dataclass
class FormError:
    message: str
    code: Union[int, str] = UNKNOW_ERROR
