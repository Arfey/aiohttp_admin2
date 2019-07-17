import re
from typing import Optional

from aiohttp_admin2.core.fields.abc import FieldABC
from aiohttp_admin2.core.constants import (
    FormError,
    EMAIL_MESSAGE_ERROR,
    EMAIL_CODE_ERROR,
)


__all__ = ['TextField', 'EmailField', 'IntegerField', ]


EMAIL_REG = '\w+[.|\w]\w+@\w+[.]\w+[.|\w+]\w+'


class TextField(FieldABC):
    """
    The base field for representation a text data.
    """
    default = ''


class IntegerField(TextField):
    """
    The base field for representation a integer type.
    """

class EmailField(TextField):
    """
    The base field for representation an email data.
    """
    email_err_message = EMAIL_MESSAGE_ERROR
    email_err_code = EMAIL_CODE_ERROR

    def validation(self) -> Optional[FormError]:
        if not re.search(EMAIL_REG, self.value):
            return FormError(
                message=self.email_err_message,
                code=self.email_err_code,
            )
