from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

from ...core.types import NoChange


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
class LineOverrides:
    """Several items, so a field may be ``NoChange`` when they disagree."""

    color : QColor      | None | NoChange = None
    width : float       | None | NoChange = None
    style : Qt.PenStyle | None | NoChange = None


@dataclass
class FillTheme:
    color : QColor
    style : Qt.BrushStyle


@dataclass
class FillOverride:
    color : QColor        | None = None
    style : Qt.BrushStyle | None = None


@dataclass
class FillOverrides:
    """Several items, so a field may be ``NoChange`` when they disagree."""

    color : QColor        | None | NoChange = None
    style : Qt.BrushStyle | None | NoChange = None


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


@dataclass
class TextOverrides:
    """
    Used where multiple items may have different text overrides,
    e.g. dialogs.
    """

    color     : QColor | None | NoChange = None
    font      : str    | None | NoChange = None
    size      : float  | None | NoChange = None
    bold      : bool   | None | NoChange = None
    italic    : bool   | None | NoChange = None
    underline : bool   | None | NoChange = None