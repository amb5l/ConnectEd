from enum        import Enum, auto
from typing      import Optional
from math        import sqrt

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QMouseEvent, QCursor, QPainterPath

from ...core import settings, _iround, LAYER_SHEET, LAYER_DRAWING

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing

class Layer(Enum):
    Sheet   = auto()
    Drawing = auto()

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
        Idle             = auto()
        ViewCenter       = auto()
        ViewPan2         = auto()
        ViewZoomWindow1  = auto()
        ViewZoomWindow2  = auto()
        SelectRectangle2 = auto()
        PlaceRectangle1  = auto()
        PlaceRectangle2  = auto()

    def _itemsRect(self: 'Drawing') -> QRectF:
        items_rect = QRectF()
        for item in self.scene.items():
            if item == self.extents or item == self.grid:
                continue
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = items_rect.united(item_rect)
        if items_rect.isEmpty():
            items_rect = self.extents.rect()
        return items_rect

    def _rubberBandRect(self: 'Drawing') -> QRectF:
        prect = self.rubber_band.geometry().normalized() # physical coords
        return QRectF(
            self.mapToScene(prect.topLeft()),
            self.mapToScene(prect.bottomRight())
        )

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

    def _setLayer(self: 'Drawing', layer: Layer) -> None:
        match layer:
            case Layer.Sheet:
                # for all scene items with Z values in sheet, set selectable
                for item in self.scene.items():
                    item.setFlag(
                        QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                        item.zValue() in LAYER_SHEET
                    )
            case Layer.Drawing:
                for item in self.scene.items():
                    item.setFlag(
                        QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                        item.zValue() in LAYER_DRAWING
                    )

    def _selectRect(self: 'Drawing', rect: QRectF) -> None:
        path = QPainterPath()
        path.addRect(rect)
        self.scene.setSelectionArea(
            path,
            Qt.ItemSelectionOperation.AddToSelection,
            Qt.ItemSelectionMode.IntersectsItemShape,
            self.transform()
        )

    def _selectPoint(self: 'Drawing', point: QPointF) -> None:
        # itemAt is not reliable for point selection
        self._selectRect(QRectF(point - QPointF(0.5, 0.5), QSizeF(1,1)))

    def _addWIP(self: 'Drawing', item: QGraphicsItem) -> None:
        self.wip = item
        self.wip.setWIP(True)
        self.scene.addItem(self.wip)

    def _completeWIP(self: 'Drawing') -> None:
        self.wip.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.wip.setWIP(False)
        self.wip = None

    def _removeWIP(self: 'Drawing') -> None:
        self.scene.removeItem(self.wip)
        self.wip = None
