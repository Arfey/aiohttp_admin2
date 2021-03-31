import typing as t

__all__ = ["Cell", "ListObject", ]


class Cell(t.NamedTuple):
    """Field data representation for html template"""
    value: t.Any
    url: t.Tuple[str, t.Dict[str, t.Union[str, int]]]
    is_safe: bool = False


class ListObject(t.NamedTuple):
    rows: t.List[t.List[Cell]]
    has_next: bool
    has_prev: bool
    count: t.Optional[int]
    active_page: t.Optional[int]
    per_page: int
    next_id: t.Optional[int]
