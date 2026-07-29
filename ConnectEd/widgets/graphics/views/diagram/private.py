from __future__ import annotations

from typing          import Self
from collections.abc import Sequence

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

from .host import asDiagramView



class DiagramViewPrivateMixin:
    @checked
    def _allItemsRect(self : Self) -> QRectF | None:
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
            return None
        items_rect = None
        for item in scene.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    @checked
    def _selectedItemsRect(self : Self) -> QRectF | None:
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
            return None
        items_rect = None
        for item in scene.selectedItems():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    @checked
    def _itemsCenter(
        self  : Self,
        items : QGraphicsItem | Sequence[QGraphicsItem]
    ) -> QPointF:
        """Return scene center of the item set."""
        if isinstance(items, QGraphicsItem):
            items = [items]
        items_rect : QRectF | None = None
        for item in items:
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        if items_rect is None:
            raise ValueError("No items")
        return items_rect.center()

    @checked
    def _pan(self : Self, delta : QPointF) -> None:
        host = asDiagramView(self)
        if (viewport := host.viewport()) is None:
            raise TypeError("No viewport")
        lrect = host.mapToScene(viewport.rect()).boundingRect()  # Scene coords
        pan = QPointF(lrect.width()  * delta.x(), lrect.height() * delta.y())
        transform = host.transform()
        pdelta = QPointF(transform.m11() * pan.x(), transform.m22() * pan.y())
        if (horizontal_scroll_bar := host.horizontalScrollBar()) is None:
            raise TypeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() - int(pdelta.x())
        )
        if (vertical_scroll_bar := host.verticalScrollBar()) is None:
            raise TypeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() - int(pdelta.y())
        )
        host._mouse_vpos = host.mapFromGlobal(QCursor.pos())
        host._mouse_spos = host.mapToScene(host._mouse_vpos)

    @checked
    def _zoomAbs(self : Self, abs : int | float) -> None:
        host = asDiagramView(self)
        abs = max(abs, settings().get("display/zoom/min"))
        abs = min(abs, settings().get("display/zoom/max"))
        host._zoom = abs
        host.resetTransform()
        host.scale(host._zoom, host._zoom)
        window().statusBar().zoom.setText(f"{host._zoom * 100:.2f}%")

    @checked
    def _zoomRel(self : Self, rel : int | float) -> None:
        host = asDiagramView(self)
        host._zoomAbs(host._zoom * rel)

    @checked
    def _zoomRelMouse(self : Self, rel : int | float) -> None:
        host = asDiagramView(self)
        vpos_old = host._mouse_vpos
        spos_old = host._mouse_spos
        host._zoomRel(rel)
        vpos_new = host.mapFromScene(spos_old)
        delta = vpos_new - vpos_old
        if (horizontal_scroll_bar := host.horizontalScrollBar()) is None:
            raise TypeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() + delta.x()
        )
        if (vertical_scroll_bar := host.verticalScrollBar()) is None:
            raise TypeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() + delta.y()
        )

    @checked
    def _zoomRect(self : Self, rect : QRectF) -> None:
        host = asDiagramView(self)
        if (viewport := host.viewport()) is None:
            raise TypeError("No viewport")
        factor = min(
            viewport.width()  / rect.width(),
            viewport.height() / rect.height()
        ) * (1 - settings().get("display/zoom/padding"))
        host._zoomAbs(factor)
        host.centerOn(rect.center())

    @checked
    def _round2nearest(self : Self, x : float, n : float) -> float:
        return round(x / n) * n

    @checked
    def _snap(self : Self, pos : QPointF) -> QPointF:
        host = asDiagramView(self)
        return QPointF(
            host._round2nearest(pos.x(), host.grid.pitch.x()),
            host._round2nearest(pos.y(), host.grid.pitch.y())
        ) if host.grid.snap else pos

    @checked
    def _distance(self : Self, cp1 : QPoint, cp2 : QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    @checked
    def _setLayer(self : Self, layer : DiagramViewLayer) -> None:
        host = asDiagramView(self)
        host.layer = layer
        if (scene := host.scene()) is None:
            return
        for item in scene.items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    @checked
    def _itemsAt(self : Self, pos : QPoint | QPointF) -> list[QGraphicsItem]:
        host = asDiagramView(self)
        if host.scene() is None:
            raise RuntimeError("No scene")
        if isinstance(pos, QPointF):
            pos = host.mapFromScene(pos)
        items = host.items(pos)
        return [
            i for i in items
            if i.zValue() in host.layer.value \
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
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
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
                host.viewportTransform()
            )
            for item in items:
                item.setSelected(not item.isSelected())
        else:
            scene.setSelectionArea(
                path,
                Qt.ItemSelectionOperation.AddToSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
                host.transform()
            )
        scene.blockSignals(False)
        scene.selectionChanged.emit()

    @checked
    def _selectClick(
        self      : Self,
        pos       : QPointF,
        modifiers : MouseModifier
    ) -> None:
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
            raise RuntimeError("No scene")
        items = [
            i for i in host._itemsAt(pos) if i.flags()
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
            menu = Menu(host)
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
                action = QAction(text, host)
                action.setData(item)
                action.triggered.connect(
                    lambda checked, item, prev=init_sel[item]:
                    _selectItem(item, prev)
                )
                menu.addAction(action)
            menu.hovered.connect(_onHover)
            menu.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            menu.setFocus()
            menu.exec(host.mapToGlobal(host.mapFromScene(pos)))
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
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
            raise RuntimeError("No scene")
        items = [
            i for i in host._itemsAt(pos) if i.flags()
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
        host = asDiagramView(self)
        if (scene := host.scene()) is None:
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
        host = asDiagramView(self)
        items = host._selectedItems(item_types)
        return items[0] if items else None
