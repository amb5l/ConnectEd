from __future__ import annotations

from typing import Self

from math  import sqrt

from PyQt6.QtCore    import Qt, QPointF, QRectF, QPoint
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QPainterPath, QAction, QCursor

from .....app import settings, window, logger

from .....core.check import checked

from ....menu import Menu

from ...items.block     import BlockItem
from ...items.block_pin import BlockPinItem, BlockPinArrowItem
from ...items.node      import FixedNodeItem

from ...items.mixin.select import ItemSelectMixin

from .defs import DiagramViewLayer

from .mouse import MouseModifier


class DiagramViewPrivateMixin:
    @checked
    def _allItemsRect(self : Self) -> QRectF | None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            return None
        items_rect = None
        for item in scene.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    @checked
    def _selectedItemsRect(self : Self) -> QRectF | None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            return None
        items_rect = None
        for item in scene.selectedItems():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    @checked
    def _pan(self : Self, delta : QPointF) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (viewport := self.viewport()) is None:
            raise TypeError("No viewport")
        lrect = self.mapToScene(viewport.rect()).boundingRect()  # Scene coords
        pan = QPointF(lrect.width()  * delta.x(), lrect.height() * delta.y())
        transform = self.transform()
        pdelta = QPointF(transform.m11() * pan.x(), transform.m22() * pan.y())
        if (horizontal_scroll_bar := self.horizontalScrollBar()) is None:
            raise TypeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() - int(pdelta.x())
        )
        if (vertical_scroll_bar := self.verticalScrollBar()) is None:
            raise TypeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() - int(pdelta.y())
        )
        self._mouse_vpos = self.mapFromGlobal(QCursor.pos())
        self._mouse_spos = self.mapToScene(self._mouse_vpos)

    @checked
    def _zoomAbs(self : Self, abs : int | float) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        abs = max(abs, settings().get("display/zoom/min"))
        abs = min(abs, settings().get("display/zoom/max"))
        self.zoom = abs
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
        window().statusBar().zoom.setText(f"{self.zoom * 100:.2f}%")

    @checked
    def _zoomRel(self : Self, rel : int | float) -> None:
        self._zoomAbs(self.zoom * rel)

    @checked
    def _zoomRelMouse(self : Self, rel : int | float) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        vpos_old = self._mouse_vpos
        spos_old = self._mouse_spos
        self._zoomRel(rel)
        vpos_new = self.mapFromScene(spos_old)
        delta = vpos_new - vpos_old
        if (horizontal_scroll_bar := self.horizontalScrollBar()) is None:
            raise TypeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() + delta.x()
        )
        if (vertical_scroll_bar := self.verticalScrollBar()) is None:
            raise TypeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() + delta.y()
        )

    @checked
    def _zoomRect(self : Self, rect : QRectF) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (viewport := self.viewport()) is None:
            raise TypeError("No viewport")
        factor = min(
            viewport.width()  / rect.width(),
            viewport.height() / rect.height()
        ) * (1 - settings().get("display/zoom/padding"))
        self._zoomAbs(factor)
        self.centerOn(rect.center())

    @checked
    def _round2nearest(self : Self, x : float, n : float) -> float:
        return round(x / n) * n

    @checked
    def _snap(self : Self, pos : QPointF) -> QPointF:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        return QPointF(
            self._round2nearest(pos.x(), self.grid.pitch.x()),
            self._round2nearest(pos.y(), self.grid.pitch.y())
        ) if self.grid.snap else pos

    @checked
    def _distance(self : Self, cp1 : QPoint, cp2 : QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    @checked
    def _setLayer(self : Self, layer : DiagramViewLayer) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.layer = layer
        if (scene := self.scene()) is None:
            return
        for item in scene.items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    @checked
    def _itemsAt(self : Self, pos : QPoint | QPointF) -> list[QGraphicsItem]:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if self.scene() is None:
            raise RuntimeError("No scene")
        if isinstance(pos, QPointF):
            pos = self.mapFromScene(pos)
        items = self.items(pos)
        return [
            i for i in items
            if i.zValue() in self.layer.value \
                and i.acceptedMouseButtons() != Qt.MouseButton.NoButton
        ]

    @checked
    def _siblingBlockPins(
        self  : Self,
        items : list[QGraphicsItem]
    ) -> list[BlockPinItem]:
        pins = []
        common_parent = None
        for item in items:
            if isinstance(item, BlockPinItem):
                item_parent = item.parentItem()
                if not isinstance(item_parent, BlockItem):
                    logger().error("Block pin item has non-block parent")
                    return []
                if common_parent is None:
                    common_parent = item_parent
                elif item_parent != common_parent:
                    return []  # multiple blocks - no go
                pins.append(item)
            elif not isinstance(item, BlockPinArrowItem | FixedNodeItem):
                return []
        return [] if common_parent is None else pins

    @checked
    def _selectRect(
        self      : Self,
        rect      : QRectF,
        modifiers : MouseModifier
    ) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            raise RuntimeError("No scene")
        toggle = modifiers & (MouseModifier.CTRL | MouseModifier.SHIFT) \
            == MouseModifier.CTRL
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

    @checked
    def _selectClick(
        self      : Self,
        pos       : QPointF,
        modifiers : MouseModifier
    ) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            raise RuntimeError("No scene")
        items = [
            i for i in self._itemsAt(pos) if i.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]
        selected_items = scene.selectedItems()
        # ctrl = toggle selection of (top) item
        # shift = add (top) item to selection set
        # alt = show a menu to choose between multiple items at point
        choice = modifiers & MouseModifier.ALT
        modifiers = modifiers & (MouseModifier.CTRL | MouseModifier.SHIFT)
        fresh = modifiers == MouseModifier.NONE
        toggle = modifiers & MouseModifier.CTRL
        # helper function
        def _selectItem(
            item : QGraphicsItem,
            prev : bool | None = None  # initial selection state if known
        ) -> None:
            prev = prev or item.isSelected()
            if fresh:
                if [item] != selected_items:
                    scene.clearSelection()
                elif isinstance(item, ItemSelectMixin) and item.isSelected():
                    item.cycleSelectMode()
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
                    _selectItem(item, init_sel[item])
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
            scene.clearSelection()

    @checked
    def _selectDrag(
        self      : Self,
        pos       : QPointF,
        modifiers : MouseModifier
    ) -> None:
        """
        Should only be called when there is an item at the given position.
        Otherwise a marquee selection is happening.
        """
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            raise RuntimeError("No scene")
        items = [
            i for i in self._itemsAt(pos) if i.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]
        # shift = add (top) item to selection set
        # (alt is used to change drag mode, ctrl is used for cloning)
        fresh = modifiers & MouseModifier.SHIFT == MouseModifier.NONE
        # perform selection
        if items:
            item = items[0]
            if fresh and not item.isSelected():
                scene.clearSelection()
            item.setSelected(True)
        else:
            # this should never happen
            logger().warning("No items at position")
            scene.clearSelection()

    @checked
    def _selectedItems(
        self       : Self,
        item_types : type | tuple[type, ...] | None = None
    ) -> list[QGraphicsItem]:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if (scene := self.scene()) is None:
            return []
        return [
            i for i in scene.selectedItems()
            if item_types is None or isinstance(i, item_types)
        ]

    @checked
    def _selectedItem(
        self       : Self,
        item_types : type | tuple[type, ...] | None
    ) -> QGraphicsItem | None:
        items = self._selectedItems(item_types)

        return items[0] if items else None
