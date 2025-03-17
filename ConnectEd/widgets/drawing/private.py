from enum   import Enum, auto
from typing import Optional
from math   import sqrt

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRect, QRectF, QTimer
from PyQt6.QtWidgets import QRubberBand, QGraphicsItem, QMenu
from PyQt6.QtGui     import QMouseEvent, QCursor, QPainterPath, \
                            QPainter, QPen, QColor, QAction, QIcon

from ...core import settings, LAYER_SHEET, LAYER_DRAWING

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing

class Layer(Enum): # TODO resolve drawing vs diagram
    Sheet   = LAYER_SHEET
    Drawing = LAYER_DRAWING

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

    def __init__(self : 'DrawingMouseButton') -> None:
        self.press   = DrawingMousePress()
        self.release = DrawingMouseRelease()
        self.double  = DrawingMousePress()
        self.state   = DrawingMouseButtonState.Idle

class DrawingMouse:
    current : DrawingPLPos
    left    : DrawingMouseButton
    middle  : DrawingMouseButton

    def __init__(self : 'DrawingMouse') -> None:
        self.current = DrawingPLPos()
        self.left    = DrawingMouseButton()
        self.middle  = DrawingMouseButton()

class MarquisRubberBand(QRubberBand):
    """
    A custom QRubberBand with a marching ants effect.
    """

    DASH_LEN = 4
    INTERVAL = 100

    offset : int
    timer  : QTimer

    def __init__(self, shape, parent=None):
        super().__init__(shape, parent)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        if self.isVisible():
            self.timer.start(self.INTERVAL)

    def animate(self):
        self.offset = (self.offset + 1) % (2 * self.DASH_LEN)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect().adjusted(0, 0, -1, -1)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(0)
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern([self.DASH_LEN, self.DASH_LEN])
        pen.setDashOffset(self.offset)
        painter.setPen(pen)
        painter.drawRect(rect)
        pen.setColor(QColor(0, 0, 0))
        pen.setDashOffset((self.offset + self.DASH_LEN) % (2 * self.DASH_LEN))
        painter.setPen(pen)
        painter.drawRect(rect)

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)
        if visible:
            self.timer.start(100)
        else:
            self.timer.stop()

class DrawingMarquis:
    parent      : 'Drawing'
    rubber_band : MarquisRubberBand
    point1      : QPoint

    def __init__(
        self   : 'DrawingMarquis', parent : 'Drawing') -> None:
        self.parent = parent
        self.rubber_band = MarquisRubberBand(
            QRubberBand.Shape.Rectangle,
            parent
        )
        self.point1      = QPoint()

    def begin(self : 'DrawingMarquis', pos : QPoint) -> None:
        self.point1 = pos
        self.rubber_band.setGeometry(pos.x(), pos.y(), 1, 1)
        self.rubber_band.show()

    def resize(self : 'DrawingMarquis', pos : QPoint) -> None:
        self.rubber_band.setGeometry(
            QRect(
                self.point1.x(), self.point1.y(),
                pos.x() - self.point1.x(),
                pos.y() - self.point1.y()
            ).normalized()
        )

    def end(self : 'DrawingMarquis', pos : QPoint) -> None:
        self.rubber_band.setGeometry(
            QRect(
                self.point1.x(), self.point1.y(),
                pos.x() - self.point1.x(),
                pos.y() - self.point1.y()
            ).normalized()
        )
        self.rubber_band.hide()
        self.point1 = None

    def rect(self : 'DrawingMarquis') -> QRectF:
        prect = self.rubber_band.geometry().normalized() # physical coords
        return QRectF(
            self.parent.mapToScene(prect.topLeft()),
            self.parent.mapToScene(prect.bottomRight())
        )

class DrawingPrivateMixin:
    """
    A mixin class that provides private methods for the Drawing class.
    """

    MouseButtonState = DrawingMouseButtonState
    Mouse            = DrawingMouse
    Marquee          = DrawingMarquis

    class State(Enum):
        Idle            = auto()
        ViewPan1        = auto()
        ViewPan2        = auto()
        ViewZoomWindow1 = auto()
        ViewZoomWindow2 = auto()
        SelectArea2     = auto()
        EditSlide1      = auto()
        EditSlide2      = auto()
        EditMove1       = auto()
        EditMove2       = auto()
        EditResize1     = auto()
        EditResize2     = auto()
        PlaceRectangle1 = auto()
        PlaceRectangle2 = auto()

    def _allItemsRect(self: 'Drawing') -> QRectF:
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
        self.main_window.actions.actionEnable(
            'viewZoomIn',  self.zoom < settings.prefs.display.zoom.limit.max
        )
        self.main_window.actions.actionEnable(
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

    def _round_to_nearest(self: 'Drawing', x : float, n : float) -> float:
        return round(x / n) * n

    def _snap(self: 'Drawing', pos: QPointF) -> QPoint:
        return QPointF(
            self._round_to_nearest(pos.x(), self.grid.pitch.x()),
            self._round_to_nearest(pos.y(), self.grid.pitch.y())
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
        self.layer = layer
        for item in self.scene.items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    def _itemsAt(self: 'Drawing', point: QPointF) -> list[QGraphicsItem]:
        items = self.scene.items(
            point,
            Qt.ItemSelectionMode.IntersectsItemShape,
            Qt.SortOrder.DescendingOrder,
            self.viewportTransform()
        )
        return [i for i in items if i.zValue() in self.layer.value]

    def _selectRect(
        self   : 'Drawing',
        rect   : QRectF,
        toggle : bool = False
    ) -> None:
        path = QPainterPath()
        path.addRect(rect)
        if toggle:
            items = self.scene.items(
                path,
                Qt.ItemSelectionMode.IntersectsItemShape,
                Qt.SortOrder.AscendingOrder,
                self.viewportTransform()
            )
            for item in items:
                item.setSelected(not item.isSelected())
        else:
            self.scene.setSelectionArea(
                path,
                Qt.ItemSelectionOperation.AddToSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
                self.transform()
            )
        for item in self.scene.selectedItems():
            if hasattr(item, 'updateGripsVisibility'):
                item.updateGripsVisibility()

    def _selectPoint(
        self   : 'Drawing',
        point  : QPointF,
        toggle : bool = False,
        choice : bool = False
    ) -> None:
        items = self._itemsAt(point)
        if len(items) > 1 and choice: # multiple choice case
            init_sel = {item: item.isSelected() for item in items}
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu::item {
                    padding: 2px 10px 2px 4px;  /* Reduce left padding */
                }
                QMenu::icon {
                    width: 0px;  /* Ensure no space for icons */
                }
            """)
            for item in items:
                text = f'{item.__class__.__name__}'
                action = QAction(text, self)
                action.setIcon(QIcon())
                action.setData(item)
                action.triggered.connect(
                    lambda checked, i=item, t=toggle, p=init_sel[item]:
                    self._select_item(i, t, p)
                )
                menu.addAction(action)
            def _on_hover(action):
                for item in items:
                    item.setSelected(init_sel[item])
                item = action.data() if action else None
                if item:
                    self._select_item(item, toggle, init_sel[item])
            menu.hovered.connect(_on_hover)
            menu.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            menu.setFocus()
            menu.exec(self.mapToGlobal(self.mapFromScene(point)))
        elif items: # single or top item case
            item = items[0]
            if toggle:
                item.setSelected(not item.isSelected())
            else:
                item.setSelected(True)
        for item in self.scene.selectedItems():
            if hasattr(item, 'updateGripsVisibility'):
                item.updateGripsVisibility()

    def _select_item(self, item, toggle, prev=None):
        if prev is None:
            item.setSelected(not item.isSelected() if toggle else True)
        else:
            item.setSelected(not prev if toggle else True)

    def _addWIP(self: 'Drawing', item: QGraphicsItem) -> None:
        self.wip      = item
        self.prev_pos = item.pos()
        self.scene.addItem(self.wip)

    def _completeWIP(self: 'Drawing') -> None:
        self.wip.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.wip.update()
        self.wip      = None
        self.prev_pos = None

    def _removeWIP(self: 'Drawing') -> None:
        self.scene.removeItem(self.wip)
        self.wip      = None
        self.prev_pos = None
