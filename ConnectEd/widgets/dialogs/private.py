from __future__ import annotations

from typing import Any

from ...core.check import checked
from ...core.types import NO_CHANGE

from ..graphics.presentation import LineTheme, LineOverrides, \
                                    FillTheme, FillOverrides, \
                                    TextTheme, TextOverrides


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.mixin.presentation import ItemPresentationMixin


@checked
def _combinedValue(
    items       : list[ItemPresentationMixin],
    method_name : str
) -> Any:
    result = None
    for item in items:
        if (method := getattr(item, method_name, None)) is not None:
            value = method()
            result = \
                value if result is None else \
                result if result == value else \
                NO_CHANGE
    return result


def _lineTheme(items : list[ItemPresentationMixin]) -> LineTheme:
    themes = [item.lineTheme() for item in items if item.hasLine()]
    if len(themes) == 0:
        raise TypeError("No line items")
    theme = themes[0]
    if any(other != theme for other in themes[1:]):
        raise TypeError("Line themes differ")
    return theme


def _lineOverrides(items : list[ItemPresentationMixin]) -> LineOverrides:
    overrides = [item.lineOverride() for item in items if item.hasLine()]
    if len(overrides) == 0:
        raise TypeError("No line items")

    def _field(name : str) -> Any:
        values = [getattr(override, name) for override in overrides]
        first = values[0]
        return first if all(value == first for value in values[1:]) else NO_CHANGE

    return LineOverrides(
        color = _field("color"),
        width = _field("width"),
        style = _field("style")
    )


def _fillTheme(items : list[ItemPresentationMixin]) -> FillTheme:
    themes = [item.fillTheme() for item in items if item.hasFill()]
    if len(themes) == 0:
        raise TypeError("No fill items")
    theme = themes[0]
    if any(other != theme for other in themes[1:]):
        raise TypeError("Fill themes differ")
    return theme


def _fillOverrides(items : list[ItemPresentationMixin]) -> FillOverrides:
    overrides = [item.fillOverride() for item in items if item.hasFill()]
    if len(overrides) == 0:
        raise TypeError("No fill items")

    def _field(name : str) -> Any:
        values = [getattr(override, name) for override in overrides]
        first = values[0]
        return first if all(value == first for value in values[1:]) else NO_CHANGE

    return FillOverrides(
        color = _field("color"),
        style = _field("style")
    )


def _textTheme(items : list[ItemPresentationMixin]) -> TextTheme:
    themes = [item.textTheme() for item in items if item.hasText()]
    if len(themes) == 0:
        raise TypeError("No text items")
    theme = themes[0]
    if any(other != theme for other in themes[1:]):
        raise TypeError("Text themes differ")
    return theme


def _textOverrides(items : list[ItemPresentationMixin]) -> TextOverrides:
    overrides = [item.textOverride() for item in items if item.hasText()]
    if len(overrides) == 0:
        raise TypeError("No text items")

    def _field(name : str) -> Any:
        values = [getattr(override, name) for override in overrides]
        first = values[0]
        return first if all(value == first for value in values[1:]) else NO_CHANGE

    return TextOverrides(
        color     = _field("color"),
        font      = _field("font"),
        size      = _field("size"),
        bold      = _field("bold"),
        italic    = _field("italic"),
        underline = _field("underline")
    )


__all__ = [
    "_combinedValue",
    "_lineTheme", "_lineOverrides",
    "_fillTheme", "_fillOverrides",
    "_textTheme", "_textOverrides"
]
