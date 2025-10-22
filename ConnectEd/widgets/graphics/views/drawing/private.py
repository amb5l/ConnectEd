from math   import sqrt

from PyQt6.QtCore    import Qt, QPointF, QRectF, QPoint
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QMouseEvent, QPainterPath, QIcon, QAction, QCursor

from .....app import settings, window

from ....menu import Menu

from ...items.block     import Block
from ...items.block_pin import BlockPin, BlockPinArrow, BlockPinEntry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


qkm = Qt.KeyboardModifier

class DrawingViewPrivateMixin:
    def _allItemsRect(self : "DrawingView") -> QRectF | None:
        items_rect = None
        for item in self.scene().items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    def _selectedItemsRect(self : "DrawingView") -> QRectF | None:
        items_rect = None
        for item in self.scene().selectedItems():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    def _pan(self : "DrawingView", delta : QPointF) -> None:
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

    def _zoomAbs(self : "DrawingView", abs : float) -> None:
        abs = max(abs, settings().get("display/zoom/min"))
        abs = min(abs, settings().get("display/zoom/max"))
        self.zoom = abs
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
        window().status_bar.zoom.setText(
            "{:.2f}%".format(self.zoom * 100)
        )


    def _zoomRel(self : "DrawingView", rel : float) -> None:
        self._zoomAbs(self.zoom * rel)

    def _zoomRelMouse(self : "DrawingView", rel : float) -> None:
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

    def _zoomRect(self : "DrawingView", rect : QRectF) -> None:
        factor = min(
            self.viewport().width()  / rect.width(),
            self.viewport().height() / rect.height()
        ) * (1 - settings().get("display/zoom/padding"))
        self._zoomAbs(factor)
        self.centerOn(rect.center())

    def _round2nearest(self : "DrawingView", x : float, n : float) -> float:
        return round(x / n) * n

    def _snap(self : "DrawingView", pos : QPointF | None) -> QPointF:
        return QPointF(0, 0) if pos is None else \
            QPointF(
                self._round2nearest(pos.x(), self.grid.pitch.x()),
                self._round2nearest(pos.y(), self.grid.pitch.y())
            ) if self.grid.snap else pos

    def _distance(self : "DrawingView", cp1 : QPoint, cp2 : QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    def _getModifiers(
        self  : "DrawingView",
        event : QMouseEvent
    ) -> Qt.KeyboardModifier:
        mask = qkm.ControlModifier | qkm.ShiftModifier | qkm.AltModifier
        return event.modifiers() & mask

    def _setLayer(self : "DrawingView", layer : "DrawingView.Layer") -> None:
        self.layer = layer
        for item in self.scene().items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    def _itemsAt(self : "DrawingView", pos : QPoint | QPointF) -> list[QGraphicsItem]:
        if isinstance(pos, QPoint):
            pos = self.mapToScene(pos)
        items = self.scene().items(
            pos,
            Qt.ItemSelectionMode.IntersectsItemShape,
            Qt.SortOrder.DescendingOrder,
            self.viewportTransform()
        )
        return [i for i in items if i.zValue() in self.layer.value]

    def _siblingBlockPins(
        self  : "DrawingView",
        items : QGraphicsItem
    ) -> list[BlockPin]:
        pins = []
        parent : Block | None = None
        for item in items:
            if isinstance(item, BlockPin):
                if parent is None:
                    parent = item.parentItem()
                elif item.parentItem() != parent:
                    return []
                pins.append(item)
            elif not isinstance(item, BlockPinArrow | BlockPinEntry):
                return []
        return [] if parent is None else pins

    def _selectRect(
        self      : "DrawingView",
        rect      : QRectF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        toggle = modifiers & (qkm.ControlModifier | qkm.ShiftModifier) \
            == qkm.ControlModifier
        path = QPainterPath()
        path.addRect(rect)
        if toggle:
            items = self.scene().items(
                path,
                Qt.ItemSelectionMode.IntersectsItemShape,
                Qt.SortOrder.AscendingOrder,
                self.viewportTransform()
            )
            for item in items:
                item.setSelected(not item.isSelected())
        else:
            self.scene().setSelectionArea(
                path,
                Qt.ItemSelectionOperation.AddToSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
                self.transform()
            )

    def _selectPoint(
        self      : "DrawingView",
        point     : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        items = self._itemsAt(point)
        toggle = modifiers & (qkm.ControlModifier | qkm.ShiftModifier) \
            == qkm.ControlModifier
        choice = modifiers & qkm.AltModifier
        if len(items) > 1 and choice: # multiple choice case
            init_sel = {item: item.isSelected() for item in items}
            menu = Menu(self)
            menu.setStyleSheet("""
                Menu::item {
                    padding: 2px 10px 2px 4px;  /* Reduce left padding */
                }
                Menu::icon {
                    width: 0px;  /* Ensure no space for icons */
                }
            """)
            for item in items:
                text = f"{item.__class__.__name__}"
                action = QAction(text, self)
                action.setIcon(QIcon())
                action.setData(item)
                action.triggered.connect(
                    lambda checked, i=item, t=toggle, p=init_sel[item]:
                    self._selectItem(i, t, p)
                )
                menu.addAction(action)
            def _onHover(action):
                for item in items:
                    item.setSelected(init_sel[item])
                item = action.data() if action else None
                if item:
                    self._selectItem(item, toggle, init_sel[item])
            menu.hovered.connect(_onHover)
            menu.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            menu.setFocus()
            menu.exec(self.mapToGlobal(self.mapFromScene(point)))
        elif items: # single or top item case
            item = items[0]
            if toggle:
                item.setSelected(not item.isSelected())
            else:
                if not item.isSelected():
                    item.setSelected(True)

    def _selectItem(self : "DrawingView", item, toggle, prev=None):
        if prev is None:
            item.setSelected(not item.isSelected() if toggle else True)
        else:
            item.setSelected(not prev if toggle else True)

    def _selectedItems(
        self  : "DrawingView",
        etype : type
    ) -> list[QGraphicsItem]:
        return [i for i in self.scene().selectedItems() if isinstance(i, etype)]

    def _selectedItem(
        self  : "DrawingView",
        etype : type
    ) -> QGraphicsItem:
        items = self._selectedItems(etype)
        return items[0] if items else None
