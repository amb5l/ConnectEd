from enum        import Enum, auto
from dataclasses import dataclass, field
from typing      import Optional
from math        import sqrt, copysign

from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QSize, QSizeF
from PyQt6.QtGui  import QMouseEvent

from ...core import settings, _iround

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing

@dataclass
class DrawingPos:
    """
    A class that holds the logical and physical coordinates of a position in a
    drawing widget.
    """
    physical : Optional[QPoint] = None
    logical  : Optional[QPointF] = None

class DrawingRect:
    """
    A class that holds the logical and physical coordinates of a rectangle in a
    drawing widget.
    """
    physical : QRect
    logical  : QRectF
    _parent  : 'Drawing'

    def __init__(self, parent, rect : Optional[QRect | QRectF] = None) -> None:
        self._parent = parent
        if isinstance(rect, QRect):
            self.setPhysical(rect)
        elif isinstance(rect, QRectF):
            self.setLogical(rect)
        else:
            self.physical = QRect()
            self.logical  = QRectF()

    def setPhysical(self, rect : QRect) -> None:
        self.physical = rect
        self.logical = self._parent._p2lRect(rect)

    def setLogical(self, rect : QRectF) -> None:
        self.logical = rect
        self.physical = self._parent._l2pRect(rect)

class DrawingMouseState(Enum):
    Idle     = auto()
    Pressed  = auto()
    Dragging = auto()

@dataclass
class DrawingMousePress:
    physical : QPoint  = field(default_factory=QPoint)
    logical  : QPointF = field(default_factory=QPointF)

@dataclass
class DrawingMouseRelease:
    physical : QPoint  = field(default_factory=QPoint)
    logical  : QPointF = field(default_factory=QPointF)
    drag     : bool    = False

@dataclass
class DrawingMousePressRelease:
    press   : DrawingMousePress   = field(default_factory=DrawingMousePress)
    release : DrawingMouseRelease = field(default_factory=DrawingMouseRelease)

@dataclass
class DrawingMouseButton(DrawingMousePressRelease):
    state: DrawingMouseState = DrawingMouseState.Idle

class DrawingMouse:
    """A class that tracks the mouse position and button state."""

    current : DrawingPos
    left    : DrawingMouseButton
    middle  : DrawingMouseButton
    _parent : 'Drawing'

    def __init__(self : 'DrawingMouse', parent : 'Drawing') -> None:
        self._parent = parent
        self.current = DrawingPos()
        self.left    = DrawingMouseButton()
        self.middle  = DrawingMouseButton()

    def setPos(self : 'DrawingMouse', pos : QPoint | QPointF) -> None:
        if isinstance(pos, QPoint):
            self.current.physical = pos
            self.current.logical = self._parent._p2lPoint(self.current.physical)
        else:
            self.current.logical = pos
            self.current.physical = self._dp2cp(self.current.logical)

class DrawingPrivateMixin:

    MIN_SIZE = 10

    Pos               = DrawingPos
    Rect              = DrawingRect
    MouseState        = DrawingMouseState
    MousePress        = DrawingMousePress
    MouseRelease      = DrawingMouseRelease
    MousePressRelease = DrawingMousePressRelease
    MouseButton       = DrawingMouseButton
    Mouse             = DrawingMouse

    class State(Enum):
        Idle            = auto()
        ViewZoomWindow1 = auto()
        ViewZoomWindow2 = auto()
        PlaceText       = auto() # ready to place
        PlaceBlock1     = auto() # ready to place first point
        PlaceBlock2     = auto() # ready to place second point

    def _p2lPoint(self: 'Drawing', point: QPoint) -> QPointF:
        assert isinstance(point, QPoint)
        return (QPointF(point) / self.zoom) + self.pan

    def _l2pPoint(self: 'Drawing', point: QPointF) -> QPoint:
        assert isinstance(point, QPointF)
        return QPoint((point - self.pan) * self.zoom)

    def _p2lSize(self: 'Drawing', size: QSize) -> QSizeF:
        assert isinstance(size, QSize)
        return QSizeF(size) / self.zoom

    def _l2pSize(self: 'Drawing', size: QSizeF) -> QSize:
        assert isinstance(size, QSizeF)
        return QSize(size * self.zoom)

    def _p2lRect(self: 'Drawing', rect: QRect) -> QRectF:
        assert isinstance(rect, QRect)
        return QRectF(self._p2lPoint(rect.topLeft()), self._p2lSize(rect.size()))

    def _l2pRect(self: 'Drawing', rect: QRectF) -> QRect:
        assert isinstance(rect, QRectF)
        return QRect(self._l2pPoint(rect.topLeft()), self._l2pSize(rect.size()))

    def _viewUpdate(self: 'Drawing') -> None:
        #if self.mouse.current:
        #    self.main_window.status_bar.xy.setText(
        #        str(int(self.mouse.current.dpos.x())) + ',' +
        #        str(int(self.mouse.current.dpos.y()))
        #    )
        #else:
        #    self.main_window.status_bar.xy.setText('?,?')
        self.view_rect.setPhysical(self.visibleRegion().boundingRect())
        self.main_window.status_bar.zoom.setText('{:.2f}%'.format(self.zoom * 100))
        self.update()

    def _zoomUpdate(self: 'Drawing') -> None:
        self.main_window.commands.actions.actionEnable('viewZoomIn',  self.zoom < settings.prefs.display.zoom.limit.max)
        self.main_window.commands.actions.actionEnable('viewZoomOut', self.zoom > settings.prefs.display.zoom.limit.min)
        self._viewUpdate()

    def _zoomLRect(self: 'Drawing', lrect : QRectF | QRect) -> None:
        # TODO change to QRectF only
        if isinstance(lrect, QRect):
            lrect = QRectF(lrect)
        os = settings.prefs.display.overscan
        zoom_x = ( self.width()  - ( os.left + os.right  )) / lrect.width()
        zoom_y = ( self.height() - ( os.top  + os.bottom )) / lrect.height()
        self.zoom = min(zoom_x, zoom_y)
        self.pan = lrect.topLeft() - (QPointF(os.left, os.top) * self.zoom)
        self._zoomUpdate()

    def _zoomPanMouse(self: 'Drawing', zoom : Optional[float] = None) -> None:
        if zoom is None:
            zoom = self.zoom
        mdpf = QPointF(self.mouse.current.logical)
        self.pan = mdpf - ((mdpf - self.pan) * self.zoom / zoom)
        self.zoom = zoom
        self._zoomUpdate()

    def _pan(self: 'Drawing', lpoint : QPointF) -> None:
        self.pan = lpoint - (QPointF(self.rect().center()) / self.zoom)
        self._viewUpdate()

    def _snap(self: 'Drawing', pos: QPoint) -> QPoint:
        return QPoint(_iround(pos.x(), self.grid.x), _iround(pos.y(), self.grid.y)) \
            if settings.prefs.display.grid.snap else pos

    def _scalarDistance(self: 'Drawing', cp1: QPoint, cp2: QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    def _normMinRect(self: 'Drawing', dp1: QPoint, dp2: QPoint, min: int = MIN_SIZE) -> QRect:
        dx = dp2.x() - dp1.x()
        dp2.setX(dp1.x() + int(copysign(max(abs(dx), min), dx)))
        dy = dp2.y() - dp1.y()
        dp2.setY(dp1.y() + int(copysign(max(abs(dy), min), dy)))
        r = QRect()
        r.setLeft(dp1.x() if dp1.x() < dp2.x() else dp2.x())
        r.setTop(dp1.y() if dp1.y() < dp2.y() else dp2.y())
        r.setWidth(abs(dp2.x() - dp1.x()))
        r.setHeight(abs(dp2.y() - dp1.y()))
        return r

    def _getModifiers(self: 'Drawing', event: QMouseEvent) -> Qt.KeyboardModifier:
        r = event.modifiers() & Qt.KeyboardModifier.ShiftModifier  \
          | event.modifiers() & Qt.KeyboardModifier.ControlModifier \
          | event.modifiers() & Qt.KeyboardModifier.AltModifier
        return r
