from enum        import Enum, auto
from typing      import Optional
from math        import sqrt, copysign

from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QSize, QSizeF
from PyQt6.QtGui  import QMouseEvent, QCursor

from ...core import settings, _iround

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing

class DrawingPos:
    """
    A class that holds the logical and physical coordinates of a position in a
    drawing widget.
    """
    physical : Optional[QPoint] = None
    logical  : Optional[QPointF] = None
    _parent  : 'Drawing'

    def __init__(
        self   : 'DrawingPos',
        parent : 'Drawing',
        pos    : QPoint | QPointF | None = None
    ) -> None:
        self._parent = parent
        self.set(pos)

    def set(
        self : 'DrawingPos',
        pos  : QPoint | QPointF | None = None
    ) -> None:
        if isinstance(pos, QPoint):
            self.physical = pos
            self.logical  = self._parent._p2lPoint(pos)
        elif isinstance(pos, QPointF):
            self.logical  = pos
            self.physical = self._parent._l2pPoint(pos)
        elif pos is None:
            self.physical = None
            self.logical  = None
        else:
            raise ValueError(f"Invalid position type: {type(pos)}")

    def clear(self : 'DrawingPos') -> None:
        self.physical = None
        self.logical  = None

class DrawingRect:
    """
    A class that holds the logical and physical coordinates of a rectangle in a
    drawing widget.
    """
    physical : QRect
    logical  : QRectF
    _parent  : 'Drawing'

    def __init__(
        self   : 'DrawingRect',
        parent : 'Drawing',
        rect   : Optional[QRect | QRectF] = None
    ) -> None:
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

class DrawingMousePress(DrawingPos):
    modifiers : Qt.KeyboardModifier

    def __init__(
        self      : 'DrawingMousePress',
        parent    : 'Drawing',
        pos       : QPoint | QPointF | None = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(parent, pos)
        self.modifiers = modifiers

    def set(
        self      : 'DrawingMousePress',
        pos       : QPoint | QPointF | None = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().set(pos)
        self.modifiers = modifiers

    def clear(self : 'DrawingMousePress'):
        super().clear()
        self.modifiers = Qt.KeyboardModifier.NoModifier

class DrawingMouseRelease(DrawingPos):
    pass

class DrawingMouseButtonState(Enum):
    Idle     = auto()
    Pressed  = auto()
    Dragging = auto()

class DrawingMouseButton:
    prev    : DrawingPos               # previous click position
    press   : DrawingMousePress        # latest press position + modifiers
    release : DrawingMouseRelease      # latest release position + drag state
    state   : DrawingMouseButtonState

    def __init__(self : 'DrawingMouseButton', parent : 'Drawing') -> None:
        self.prev    = DrawingPos(parent)
        self.press   = DrawingMousePress(parent)
        self.release = DrawingMouseRelease(parent)
        self.state   = DrawingMouseButtonState.Idle

    def setPress(
        self      : 'DrawingMouseButton',
        pos       : QPoint | QPointF,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        self.prev.physical = self.press.physical
        self.prev.logical  = self.press.logical
        self.press.set(pos, modifiers)

    def setRelease(
        self : 'DrawingMouseButton',
        pos  : QPoint | QPointF
    ) -> None:
        self.release.set(pos)

    def clear(self : 'DrawingMouseButton') -> None:
        self.prev.clear()
        self.press.clear()
        self.release.clear()
        self.state = DrawingMouseButtonState.Idle

class DrawingMouse:
    """A class that tracks the mouse position and button state."""

    current : DrawingPos
    left    : DrawingMouseButton
    middle  : DrawingMouseButton
    _parent : 'Drawing'

    def __init__(self : 'DrawingMouse', parent : 'Drawing') -> None:
        self._parent = parent
        self.current = DrawingPos(parent)
        self.left    = DrawingMouseButton(parent)
        self.middle  = DrawingMouseButton(parent)

    def setPos(self : 'DrawingMouse', pos : QPoint | QPointF) -> None:
        if isinstance(pos, QPoint):
            self.current.physical = pos
            self.current.logical = self._parent._p2lPoint(self.current.physical)
        else:
            self.current.logical = pos
            self.current.physical = self._dp2cp(self.current.logical)

class DrawingPrivateMixin:
    """
    A mixin class that provides private methods for the Drawing class.
    """

    PLPos             = DrawingPos
    PLRect            = DrawingRect
    MouseButtonState  = DrawingMouseButtonState
    MousePress        = DrawingMousePress
    MouseRelease      = DrawingMouseRelease
    MouseButton       = DrawingMouseButton
    Mouse             = DrawingMouse

    class State(Enum):
        Idle            = auto()
        ViewCenter      = auto()
        ViewPan1        = auto()
        ViewPan2        = auto()
        ViewZoomWindow1 = auto()
        ViewZoomWindow2 = auto()

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

    def _zoomUpdate(self: 'Drawing') -> None:
        self.main_window.status_bar.zoom.setText('{:.2f}%'.format(self.zoom * 100))
        self.main_window.commands.actions.actionEnable('viewZoomIn',  self.zoom < settings.prefs.display.zoom.limit.max)
        self.main_window.commands.actions.actionEnable('viewZoomOut', self.zoom > settings.prefs.display.zoom.limit.min)
        self._panUpdate()

    def _panUpdate(self: 'Drawing') -> None:
        self.update()
        self._panStatusBar()

    def _panStatusBar(self: 'Drawing') -> None:
        mouse_lpos = self._p2lPoint(self.mapFromGlobal(QCursor.pos()))
        self.main_window.status_bar.xy.setText(
            str(int(mouse_lpos.x())) + ',' + str(int(mouse_lpos.y()))
        )

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

    def _zoomPRect(self: 'Drawing', prect : QRect) -> None:
        self._zoomLRect(self._p2lRect(prect))

    def _zoomPanMouse(self: 'Drawing', zoom : Optional[float] = None) -> None:
        if zoom is None:
            zoom = self.zoom
        mdpf = QPointF(self.mouse.current.logical)
        self.pan = mdpf - ((mdpf - self.pan) * self.zoom / zoom)
        self.zoom = zoom
        self._zoomUpdate()

    def _center(self: 'Drawing', lpoint : QPointF) -> None:
        self.pan = lpoint - (QPointF(self.rect().center()) / self.zoom)
        self._panUpdate()

    def _snap(self: 'Drawing', pos: QPoint) -> QPoint:
        return QPoint(_iround(pos.x(), self.grid.x), _iround(pos.y(), self.grid.y)) \
            if settings.prefs.display.grid.snap else pos

    def _distance(self: 'Drawing', cp1: QPoint, cp2: QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    def _normMinRect(self: 'Drawing', dp1: QPoint, dp2: QPoint, min: int = 1) -> QRect:
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
