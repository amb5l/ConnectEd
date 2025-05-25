__all__ = ["DrawingView", "DrawingSubWindow"]

from typing import Self, Optional
from enum   import Enum, auto
from math   import ceil

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, \
                            QGraphicsView, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui     import QPainter, QPen, QCloseEvent, QKeyEvent

from .....core import LAYER_SHEET, LAYER_DRAWING

from ....marquee import Marquee

from ...scenes import DrawingScene

from .mouse   import DrawingViewMouseMixin
from .private import DrawingViewPrivateMixin
from .edit    import DrawingViewEditMixin
from .view    import DrawingViewViewMixin
from .place   import DrawingViewPlaceMixin

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

class DrawingView(
    DrawingViewMouseMixin,
    QGraphicsView,
    DrawingViewEditMixin,
    DrawingViewViewMixin,
    DrawingViewPlaceMixin,
    DrawingViewPrivateMixin
):

    Layer            = DrawingViewLayer
    Grid             = DrawingViewGrid
    PLPos            = DrawingViewPLPos
    MousePress       = DrawingViewMousePress
    MouseRelease     = DrawingViewMouseRelease
    MouseButtonState = DrawingViewMouseButtonState
    MouseButton      = DrawingViewMouseButton
    Mouse            = DrawingViewMouse
    State            = DrawingViewState
    StateTip         = DrawingViewStateTip
    Wip              = DrawingViewWip

    _shown   : bool = False
    _zoomed  : bool = False
    marquee  : Marquee
    layer    : DrawingViewLayer
    zoom     : float
    grid     : "DrawingView.Grid"
    mouse    : "DrawingView.Mouse"
    state    : "DrawingView.State"
    wip      : "DrawingView.Wip"

    def __init__(self : Self, scene : DrawingScene) -> None:
        super().__init__(scene)
        scene.textEditingComplete.connect(self.placeTextBlockFinalize)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self._shown   = False
        self._zoomed  = False
        self.marquee  = Marquee(self)
        self.layer    = DrawingViewLayer.Drawing
        self.zoom     = 1.0
        self.grid     = self.Grid()
        self.mouse    = self.Mouse()
        self.wip      = self.Wip()

        self._goState(self.State.Idle)

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(DrawingViewLayer.Drawing)

    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self._shown = True
        self.viewZoomAll()

    def resizeEvent(self : Self, event : QEvent) -> None:
        super().resizeEvent(event)
        if self._shown and not self._zoomed:
            self._zoomed = True
            self.viewZoomAll()

    def drawForeground(self : Self, painter : QPainter, rect : QRectF) -> None:
        # draw grid
        def align(x : float, px : float) -> float:
            return px * int(x / px)
        if self.grid.display:
            pp = self.transform().map(self.grid.pitch)
            px = self.grid.pitch.x()
            if pp.x() < self.grid.min_pixels:
                px *= ceil(self.grid.min_pixels / pp.x())
            py = self.grid.pitch.y()
            if pp.y() < self.grid.min_pixels:
                py *= ceil(self.grid.min_pixels / pp.y())
            grect = QRectF(
                QPointF(rect.topLeft())     - QPointF(px, py),
                QPointF(rect.bottomRight()) + QPointF(px, py)
            ).toRect()
            color = hub.settings.getTheme("grid/line")
            color.setAlpha(self.grid.alpha)
            painter.setPen(QPen(color, 0, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if self.grid.dots:
                x = align(grect.left(), px)
                while x <= grect.right():
                    y = align(grect.top(), py)
                    while y <= grect.bottom():
                        painter.drawPoint(QPointF(x, y))
                        y += py
                    x += px
            else:
                x = align(grect.left(), px)
                while x <= grect.right():
                    painter.drawLine(
                        QPointF(x, grect.top()),
                        QPointF(x, grect.bottom())
                    )
                    x += px
                y = align(grect.top(), py)
                while y <= grect.bottom():
                    painter.drawLine(
                        QPointF(grect.left(), y),
                        QPointF(grect.right(), y)
                    )
                    y += py

    def keyPressEvent(self : Self, event : QKeyEvent) -> None:
        """Override default arrow key handling to prevent panning"""
        if event.key() in (
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down
        ):
            focus_item = self.scene().focusItem()
            if (isinstance(focus_item, QGraphicsTextItem) and
                focus_item.textInteractionFlags() & Qt.TextInteractionFlag.TextEditable):
                super().keyPressEvent(event)
                event.accept()
            else:
                event.ignore()
            return
        super().keyPressEvent(event)

class DrawingSubWindow(QMdiSubWindow):
    def __init__(
        self   : Self,
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self, event: QCloseEvent) -> None:
        if isinstance(self.widget(), DrawingView):
            scene = self.widget().scene()
            if scene and scene.undo_stack:
                try:
                    scene.undo_stack.canUndoChanged.disconnect()
                    scene.undo_stack.canRedoChanged.disconnect()
                    scene.selectionChanged.disconnect()
                except TypeError:
                    pass
        hub.main_window.menu_bar.updateWindowMenu()
        super().closeEvent(event)
