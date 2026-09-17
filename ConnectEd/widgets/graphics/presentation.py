from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


@dataclass
class LineTheme:
    color : QColor
    width : float
    style : Qt.PenStyle


@dataclass
class LineOverride:
    color : QColor      | None = None
    width : float       | None = None
    style : Qt.PenStyle | None = None


@dataclass
class FillTheme:
    color : QColor
    style : Qt.BrushStyle


@dataclass
class FillOverride:
    color : QColor        | None = None
    style : Qt.BrushStyle | None = None


@dataclass
class TextTheme:
    color     : QColor
    font      : str
    size      : float
    bold      : bool
    italic    : bool
    underline : bool

@dataclass
class TextOverride:
    color     : QColor | None = None
    font      : str    | None = None
    size      : float  | None = None
    bold      : bool   | None = None
    italic    : bool   | None = None
    underline : bool   | None = None
