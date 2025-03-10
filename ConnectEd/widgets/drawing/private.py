from enum        import Enum, auto
from typing      import Optional
from math        import sqrt

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QMouseEvent, QCursor

from ...core import settings, _iround

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing

class DrawingPLPos:
    physical : Optional[QPoint] = None
    logical  : Optional[QPointF] = None

    def __init__(
        self     : 'DrawingPLPos',
        physical : Optional[QPoint] = None,
        logical  : Optional[QPointF] = None
    ) -> None:
        self.physical = physical
        self.logical  = logical

    def setPL(self, physical: QPoint, logical: QPointF) -> None:
        self.physical = physical
        self.logical  = logical

class DrawingMousePress(DrawingPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    def __init__(
        self      : 'DrawingMousePress',
        physical  : Optional[QPoint] = None,
        logical   : Optional[QPointF] = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(physical, logical)
        self.modifiers = modifiers

class DrawingMouseRelease(DrawingPLPos):
    pass

class DrawingMouseButtonState(Enum):
    Idle     = auto()
    Pressed  = auto()
    Dragging = auto()

class DrawingMouseButton:
    press   : DrawingMousePress
    release : DrawingMouseRelease
    double  : DrawingMousePress
    state   : DrawingMouseButtonState

    def __init__(
        self    : 'DrawingMouseButton',
        press   : DrawingMousePress   = DrawingMousePress(),
        release : DrawingMouseRelease = DrawingMouseRelease(),
        double  : DrawingMousePress   = DrawingMousePress()
    ) -> None:
        self.press   = DrawingMousePress()
        self.release = DrawingMouseRelease()
        self.double  = DrawingMousePress()
        self.state   = DrawingMouseButtonState.Idle

class DrawingMouse:
    current : DrawingPLPos
    left    : DrawingMouseButton
    middle  : DrawingMouseButton

    def __init__(
        self    : 'DrawingMouse',
        current : DrawingPLPos       = DrawingPLPos(),
        left    : DrawingMouseButton = DrawingMouseButton(),
        middle  : DrawingMouseButton = DrawingMouseButton()
    ) -> None:
        self.current = current
        self.left    = left
        self.middle  = middle

class DrawingPrivateMixin:
    """
    A mixin class that provides private methods for the Drawing class.
    """

    PLPos             = DrawingPLPos
    MouseButtonState  = DrawingMouseButtonState
    MousePress        = DrawingMousePress
    MouseRelease      = DrawingMouseRelease
    MouseButton       = DrawingMouseButton
    Mouse             = DrawingMouse

    class State(Enum):
        Idle            = auto()
        ViewCenter      = auto()
        ViewPan2        = auto()
        ViewZoomWindow1 = auto()
        ViewZoomWindow2 = auto()
        PlaceRectangle1 = auto()
        PlaceRectangle2 = auto()

    def _minExtents(self: 'Drawing') -> QRectF:
        rect = QRectF(self.sheet.boundingRect())
        rect.setTopLeft(-QPointF(
            self.sheet.boundingRect().width(),
            self.sheet.boundingRect().height()
        ))
        rect.setWidth(self.sheet.boundingRect().width() * 3)
        rect.setHeight(self.sheet.boundingRect().height() * 3)
        return rect

    def _boundingRect(self: 'Drawing') -> QRectF:
        items_rect = QRectF()
        for item in self.scene.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = items_rect.united(item_rect)
        return items_rect

    def _pan(self: 'Drawing', delta: QPointF) -> None:
        lrect = self.mapToScene(self.viewport().rect()).boundingRect()  # Scene coords
        pan = QPointF(lrect.width()  * delta.x(), lrect.height() * delta.y())
        transform = self.transform()
        pdelta = QPointF(transform.m11() * pan.x(), transform.m22() * pan.y())
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() - int(pdelta.x())
        )
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - int(pdelta.y())
        )
        self.mouse.current.setPL(
            self.mapFromGlobal(QCursor.pos()),
            self.mapToScene(self.mouse.current.physical)
        )

    def _zoomAbs(self: 'Drawing', abs: float) -> None:
        abs = max(abs, settings.prefs.display.zoom.limit.min)
        abs = min(abs, settings.prefs.display.zoom.limit.max)
        self.zoom = abs
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
        self.main_window.status_bar.zoom.setText(
            '{:.2f}%'.format(self.zoom * 100)
        )
        self.main_window.commands.actions.actionEnable(
            'viewZoomIn',  self.zoom < settings.prefs.display.zoom.limit.max
        )
        self.main_window.commands.actions.actionEnable(
            'viewZoomOut', self.zoom > settings.prefs.display.zoom.limit.min
        )
        self.scene.update()

    def _zoomRel(self: 'Drawing', rel: float) -> None:
        self._zoomAbs(self.zoom * rel)

    def _zoomRelMouse(self: 'Drawing', rel: float) -> None:
        ppos_old = self.mouse.current.physical
        lpos_old = self.mouse.current.logical
        self._zoomRel(rel)
        ppos_new = self.mapFromScene(lpos_old)
        delta = ppos_new - ppos_old
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() + delta.x()
        )
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() + delta.y()
        )
        self.mouse.current.setPL(
            self.mapFromGlobal(QCursor.pos()),
            self.mapToScene(self.mouse.current.physical)
        )

    def _zoomRect(self: 'Drawing', rect : QRectF) -> None:
        zoom = QPointF(
            self.viewport().width()  / rect.width(),
            self.viewport().height() / rect.height()
        )
        factor = min(zoom.x(), zoom.y()) * \
            (1 - settings.prefs.display.zoom.padding)
        self._zoomAbs(factor)
        self.centerOn(rect.center())

        # Ensure rectangles remain visible after zooming
        self.scene.update()

    def _snap(self: 'Drawing', pos: QPoint) -> QPoint:
        return QPointF(
            _iround(pos.x(), self.grid.pitch.x()),
            _iround(pos.y(), self.grid.pitch.y())
        ) if self.grid.snap else pos

    def _distance(self: 'Drawing', cp1: QPoint, cp2: QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    def _getModifiers(
        self: 'Drawing',
        event: QMouseEvent
    ) -> Qt.KeyboardModifier:
        qkm = Qt.KeyboardModifier
        mask = qkm.ControlModifier | qkm.ShiftModifier | qkm.AltModifier
        return event.modifiers() & mask

    def _addWIP(self: 'Drawing', item: QGraphicsItem) -> None:
        self.wip = item
        self.wip.setWIP(True)
        self.scene.addItem(self.wip)
        self.scene.update()

    def _completeWIP(self: 'Drawing') -> None:
        self.wip.setWIP(False)
        self.wip = None
        self.scene.update()

    def _removeWIP(self: 'Drawing') -> None:
        self.scene.removeItem(self.wip)
        self.wip = None
        self.scene.update()
