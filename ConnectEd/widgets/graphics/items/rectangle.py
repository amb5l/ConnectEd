from .role import DecorativeItem

from .base_rect import BaseRectangleItem


class RectangleItem(DecorativeItem, BaseRectangleItem):
    # instance attributes
    _line_color = None  # enable per-item appearance control
    _line_width = None  # enable per-item appearance control
    _line_style = None  # enable per-item appearance control
    _fill_color = None  # enable per-item appearance control
    _fill_style = None  # enable per-item appearance control
