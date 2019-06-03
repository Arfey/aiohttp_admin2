__all__ = ['ModelView', ]

PAGE_COUNT = 1


class ModelView:
    """
    docs
    """
    name = None

    def __init__(self):
        if not self.name:
            global PAGE_COUNT
            self.name = "Template #%s}" % PAGE_COUNT
            PAGE_COUNT += 1
