from typing import Self
from enum import Enum, auto

from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.defs import LAYER_SHEET, LAYER_DRAWING

from .....app import settings


class DrawingViewLayer(Enum):
    Sheet   = LAYER_SHEET
    Drawing = LAYER_DRAWING

class DrawingViewGrid:
    display    : bool
    snap       : bool
    pitch      : QPointF
    dots       : bool
    alpha      : int
    min_pixels : int

    def __init__(self : Self) -> None:
        s = settings().get("defaults/grid")
        self.display    = s.display
        self.snap       = s.snap
        self.pitch      = s.pitch
        self.dots       = s.dots
        self.alpha      = s.alpha
        self.min_pixels = s.min_pixels

class DrawingViewPLPos:
    physical : QPoint  | None = None
    logical  : QPointF | None = None

    def __init__(
        self     : Self,
        physical : QPoint  | None = None,
        logical  : QPointF | None = None
    ) -> None:
        self.physical = physical
        self.logical  = logical

    def setPL(self : Self, physical: QPoint, logical: QPointF) -> None:
        self.physical = physical
        self.logical  = logical

class DrawingViewMouseCurrent(DrawingViewPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    def __init__(
        self      : Self,
        physical  : QPoint  | None = None,
        logical   : QPointF | None = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(physical, logical)
        self.modifiers = modifiers

class DrawingViewMousePress(DrawingViewPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    def __init__(
        self      : Self,
        physical  : QPoint  | None = None,
        logical   : QPointF | None = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(physical, logical)
        self.modifiers = modifiers

class DrawingViewMouseRelease(DrawingViewMousePress):
    pass

class DrawingViewMouseButtonState(Enum):
    Idle     = auto()
    Pressed  = auto()
    Dragging = auto()

class DrawingViewMouseButton:
    press   : DrawingViewMousePress
    release : DrawingViewMouseRelease
    double  : DrawingViewMousePress
    state   : DrawingViewMouseButtonState

    def __init__(self : Self) -> None:
        self.press   = DrawingViewMousePress()
        self.release = DrawingViewMouseRelease()
        self.double  = DrawingViewMousePress()
        self.state   = DrawingViewMouseButtonState.Idle

class DrawingViewMouse:
    current : DrawingViewMouseCurrent
    left    : DrawingViewMouseButton
    middle  : DrawingViewMouseButton

    def __init__(self : Self) -> None:
        self.current = DrawingViewPLPos()
        self.left    = DrawingViewMouseButton()
        self.middle  = DrawingViewMouseButton()

class DrawingViewWip:
    macro     : bool
    elements  : list[QGraphicsItem] | None
    pos       : QPointF | QPoint | None
    pos0      : QPointF | QPoint | None     # start position e.g. for ortho
    selection : list[QGraphicsItem] | None
    slide     : bool | None

    def __init__(self : Self) -> None:
        self.clear()

    def clear(self : Self) -> None:
        self.macro     = False
        self.elements  = None
        self.pos       = None
        self.pos0      = None
        self.selection = None

    @property
    def element(self : Self) -> QGraphicsItem | None:
        return \
            None if self.elements is None else \
            self.elements[0] if len(self.elements) == 1 else \
            None

    @element.setter
    def element(self : Self, element : QGraphicsItem) -> None:
        self.elements = [element]
