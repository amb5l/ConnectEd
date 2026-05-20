from math import sqrt

from PyQt6.QtCore    import Qt, QPointF, QRectF, QPoint
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QMouseEvent, QPainterPath, QAction, QCursor

from .....app import settings, window, logger

from ....menu import Menu

from ...items.block     import BlockItem
from ...items.polyline  import PolylineItem
from ...items.block_pin import BlockPinItem, BlockPinArrowItem
from ...items.node      import FixedNodeItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene
    from . import DrawingView


qkm = Qt.KeyboardModifier


class DrawingViewPrivateMixin:
    def _allItemsRect(self : "DrawingView") -> QRectF | None:
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return None
        items_rect = None
        for item in scene.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    def _selectedItemsRect(self : "DrawingView") -> QRectF | None:
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return None
        items_rect = None
        for item in scene.selectedItems():
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
        window().statusBar().zoom.setText(f"{self.zoom * 100:.2f}%")

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
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return
        for item in scene.items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    def _itemsAt(
        self : "DrawingView", pos : QPoint | QPointF) -> list[QGraphicsItem]:
        if self.scene() is None:
            return []
        if isinstance(pos, QPointF):
            pos = self.mapFromScene(pos)
        items = self.items(pos)
        return [
            i for i in items
            if i.zValue() in self.layer.value \
                and i.acceptedMouseButtons() != Qt.MouseButton.NoButton
        ]

    def _siblingBlockPins(
        self  : "DrawingView",
        items : QGraphicsItem
    ) -> list[BlockPinItem]:
        pins = []
        parent : BlockItem | None = None
        for item in items:
            if isinstance(item, BlockPinItem):
                if parent is None:
                    parent = item.parentItem()
                elif item.parentItem() != parent:
                    return []
                pins.append(item)
            elif not isinstance(item, BlockPinArrowItem | FixedNodeItem):
                return []
        return [] if parent is None else pins

    def _selectRect(
        self      : "DrawingView",
        rect      : QRectF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return
        toggle = modifiers & (qkm.ControlModifier | qkm.ShiftModifier) \
            == qkm.ControlModifier
        path = QPainterPath()
        path.addRect(rect)
        scene.blockSignals(True)
        if toggle:
            items = scene.items(
                path,
                Qt.ItemSelectionMode.IntersectsItemShape,
                Qt.SortOrder.AscendingOrder,
                self.viewportTransform()
            )
            for item in items:
                item.setSelected(not item.isSelected())
        else:
            scene.setSelectionArea(
                path,
                Qt.ItemSelectionOperation.AddToSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
                self.transform()
            )
        scene.blockSignals(False)
        scene.selectionChanged.emit()

    def _selectClick(
        self      : "DrawingView",
        pos       : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        items = [
            i for i in self._itemsAt(pos) if i.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]
        selected_items = self.scene().selectedItems()
        # ctrl = toggle selection of (top) item
        # shift = add (top) item to selection set
        # alt = show a menu to choose between multiple items at point
        choice = modifiers & qkm.AltModifier
        modifiers = modifiers & (qkm.ControlModifier | qkm.ShiftModifier)
        fresh = modifiers == qkm.NoModifier
        toggle = modifiers == qkm.ControlModifier
        # helper function
        def _selectItem(
            item : QGraphicsItem,
            prev : bool | None = None  # initial selection state if known
        ) -> None:
            prev = prev or item.isSelected()
            if fresh:
                if [item] != selected_items:
                    self.scene().clearSelection()
                elif isinstance(item, PolylineItem) and item.isSelected():
                    item.cycleSelMode()
                    return
            item.setSelected(not prev if toggle else True)
        # perform selection
        if len(items) > 1 and choice: # multiple choice case
            # record initial selection state
            init_sel = {item: item.isSelected() for item in items}
            # build and display selection choices menu (top down item order)
            menu = Menu(self)
            menu.setStyleSheet("""
                QMenu::item {
                    padding-left: 8px;
                    padding-right: 8px;
                    padding-top: 4px;
                    padding-bottom: 4px;
                }
                QMenu::item:selected {
                    background: palette(highlight);
                    color: palette(highlighted-text);
                }
            """)
            def _onHover(action):
                for item in items:
                    item.setSelected(init_sel[item])
                item = action.data() if action else None
                if item:
                    _selectItem(item, toggle, init_sel[item])
            for item in items:
                text = f"{item.__class__.__name__.replace('Item', '')}"
                action = QAction(text, self)
                action.setData(item)
                action.triggered.connect(
                    lambda checked, item, prev=init_sel[item]:
                    _selectItem(item, prev)
                )
                menu.addAction(action)
            menu.hovered.connect(_onHover)
            menu.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            menu.setFocus()
            menu.exec(self.mapToGlobal(self.mapFromScene(pos)))
        elif items: # single or top item case
            _selectItem(items[0])
        elif fresh:
            self.scene().clearSelection()

    def _selectDrag(
        self      : "DrawingView",
        pos       : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        """
        Should only be called when there is an item at the given position.
        Otherwise a marquee selection is happening.
        """
        items = [
            i for i in self._itemsAt(pos) if i.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]
        # shift = add (top) item to selection set
        # (alt is used to change drag mode, ctrl is used for cloning)
        fresh = modifiers & qkm.ShiftModifier == qkm.NoModifier
        # perform selection
        if items:
            item = items[0]
            if fresh and not item.isSelected():
                self.scene().clearSelection()
            item.setSelected(True)
        else:
            # this should never happen
            logger().warning("No items at position")
            self.scene().clearSelection()

    def _selectedItems(
        self  : "DrawingView",
        etype : type
    ) -> list[QGraphicsItem]:
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return []
        return [i for i in scene.selectedItems() if isinstance(i, etype)]

    def _selectedItem(
        self  : "DrawingView",
        etype : type
    ) -> QGraphicsItem:
        items = self._selectedItems(etype)
        return items[0] if items else None
