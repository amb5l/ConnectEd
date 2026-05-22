from typing import Self
from enum import Enum, auto

from PyQt6.QtCore    import Qt, QPoint, QPointF

from .....core.defs import LAYERS_SHEET, LAYERS_DRAWING

from .....app import settings

from .....core.check import checked


class DrawingViewLayer(Enum):
    Sheet   = LAYERS_SHEET
    Drawing = LAYERS_DRAWING

class DrawingViewGrid:
    display    : bool
    snap       : bool
    pitch      : QPointF
    dots       : bool
    alpha      : int
    min_pixels : int

    @checked
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

    @checked
    def __init__(
        self     : Self,
        physical : QPoint  | None = None,
        logical  : QPointF | None = None
    ) -> None:
        self.physical = physical
        self.logical  = logical

    @checked
    def setPL(self : Self, physical : QPoint, logical : QPointF) -> None:
        self.physical = physical
        self.logical  = logical

class DrawingViewMouseCurrent(DrawingViewPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    @checked
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

    @checked
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

    @checked
    def __init__(self : Self) -> None:
        self.press   = DrawingViewMousePress()
        self.release = DrawingViewMouseRelease()
        self.double  = DrawingViewMousePress()
        self.state   = DrawingViewMouseButtonState.Idle

class DrawingViewMouse:
    current : DrawingViewMouseCurrent
    left    : DrawingViewMouseButton
    middle  : DrawingViewMouseButton

    @checked
    def __init__(self : Self) -> None:
        self.current = DrawingViewPLPos()
        self.left    = DrawingViewMouseButton()
        self.middle  = DrawingViewMouseButton()
