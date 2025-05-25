__all__ = [
    "DrawingViewLayer",
    "DrawingViewGrid",
    "DrawingViewPLPos",
    "DrawingViewMousePress",
    "DrawingViewMouseRelease",
    "DrawingViewMouseButtonState",
    "DrawingViewMouseButton",
    "DrawingViewMouse",
    "DrawingViewState",
    "DrawingViewStateTip",
    "DrawingViewWip",
]

from typing import Self, Optional
from enum import Enum, auto

from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core import LAYER_SHEET, LAYER_DRAWING

from ..... import hub


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
        s = hub.settings.get("defaults/grid")
        self.display    = s.display
        self.snap       = s.snap
        self.pitch      = s.pitch
        self.dots       = s.dots
        self.alpha      = s.alpha
        self.min_pixels = s.min_pixels

class DrawingViewPLPos:
    physical : Optional[QPoint] = None
    logical  : Optional[QPointF] = None

    def __init__(
        self     : Self,
        physical : Optional[QPoint] = None,
        logical  : Optional[QPointF] = None
    ) -> None:
        self.physical = physical
        self.logical  = logical

    def setPL(self : Self, physical: QPoint, logical: QPointF) -> None:
        self.physical = physical
        self.logical  = logical

class DrawingViewMousePress(DrawingViewPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    def __init__(
        self      : Self,
        physical  : Optional[QPoint] = None,
        logical   : Optional[QPointF] = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(physical, logical)
        self.modifiers = modifiers

class DrawingViewMouseRelease(DrawingViewPLPos):
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
    current : DrawingViewPLPos
    left    : DrawingViewMouseButton
    middle  : DrawingViewMouseButton

    def __init__(self : Self) -> None:
        self.current = DrawingViewPLPos()
        self.left    = DrawingViewMouseButton()
        self.middle  = DrawingViewMouseButton()

class DrawingViewState(Enum):
    Idle            = auto()
    ViewPan1        = auto()
    ViewPan2        = auto()
    ViewZoomWindow1 = auto()
    ViewZoomWindow2 = auto()
    SelectArea2     = auto()
    EditPaste       = auto()
    EditDuplicate1  = auto()
    EditDuplicate2  = auto()
    EditSlide1      = auto()
    EditSlide2      = auto()
    EditMove1       = auto()
    EditMove2       = auto()
    EditResize1     = auto()
    EditResize2     = auto()
    EditResize3     = auto()
    EditAppearance1 = auto()
    EditAppearance2 = auto()
    PlaceRectangle1 = auto()
    PlaceRectangle2 = auto()
    PlaceTextBlock1 = auto()
    PlaceTextBlock2 = auto()

DrawingViewStateTip = {
    DrawingViewState.Idle            : "Idle",
    DrawingViewState.ViewPan1        : "Pan: pick the first point",
    DrawingViewState.ViewPan2        : "Pan: pick the second point",
    DrawingViewState.ViewZoomWindow1 : "Zoom Window: pick the first point",
    DrawingViewState.ViewZoomWindow2 : "Zoom Window: pick the second point",
    DrawingViewState.SelectArea2     : "Select: complete the marquee selection",
    DrawingViewState.EditPaste       : "Paste: select the paste position",
    DrawingViewState.EditDuplicate1  : "Duplicate: select one or more items",
    DrawingViewState.EditDuplicate2  : "Duplicate: place the duplicated item(s) as required",
    DrawingViewState.EditSlide1      : "Slide: select one or more items",
    DrawingViewState.EditSlide2      : "Slide: place the selected item(s) as required",
    DrawingViewState.EditMove1       : "Move: select one or more items",
    DrawingViewState.EditMove2       : "Move: place the selected item(s) as required",
    DrawingViewState.EditResize1     : "Resize: select a single resizeable item",
    DrawingViewState.EditResize2     : "Resize: select a grip to begin resizing",
    DrawingViewState.EditResize3     : "Resize: place the selected grip as required",
    DrawingViewState.EditAppearance1 : "Appearance: select one or more items",
    DrawingViewState.EditAppearance2 : "Appearance: specify changes",
    DrawingViewState.PlaceRectangle1 : "Place Rectangle: pick the first point",
    DrawingViewState.PlaceRectangle2 : "Place Rectangle: pick the second point",
    DrawingViewState.PlaceTextBlock1 : "Place Text Block: pick a position",
    DrawingViewState.PlaceTextBlock2 : "Place Text Block: enter the text"
}

class DrawingViewWip:
    macro     : bool
    elements  : Optional[list[QGraphicsItem]]
    pos0      : Optional[QPointF | QPoint]
    selection : Optional[list[QGraphicsItem]]

    def __init__(self : Self) -> None:
        self.clear()

    def clear(self : Self) -> None:
        self.macro     = False
        self.elements  = None
        self.pos0      = None
        self.selection = None