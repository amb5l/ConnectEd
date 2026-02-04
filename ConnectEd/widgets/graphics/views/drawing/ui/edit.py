from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui     import QCursor

from ....query import QueryWindow

from ..interaction      import RotateItemMixin
from ..interaction.edit import EditMoveInteraction

from ....items import NoChange, NO_CHANGE, AlignH, AlignV

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items            import ItemMixin
    from ....items.text       import TextItem
    from ....items.grip       import ResizeGripItem
    from ....items.symbol_pin import SymbolPinItem
    from .                    import DrawingViewUi


class DrawingViewUiEditMixin:
    def editUndo(self : "DrawingViewUi") -> None:
        self._scene.undo()

    def editRedo(self : "DrawingViewUi") -> None:
        self._scene.redo()

    def editRepeat(self : "DrawingViewUi") -> None:
        raise NotImplementedError("editRepeat not implemented")

    def editCancel(self : "DrawingViewUi") -> None:
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = None
        self._scene.clearSelection()
        self._view.state.go(self._view.stateIdle)

    def editCut(self : "DrawingViewUi") -> None:
        self._scene.editCut(
            self._snap(self._view.mouse.current.logical), undoable=True
        )

    def editCopy(self : "DrawingViewUi") -> None:
        self._scene.editCopy(self._snap(self._view.mouse.current.logical))

    def editPaste(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditPaste)

    def editDelete(self : "DrawingViewUi") -> None:
        self._scene.editDelete(undoable=True)

    def editDuplicate(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditDuplicate)

    def editSelectArea(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditSelectArea1)

    def editSelectAll(self : "DrawingViewUi") -> None:
        self._scene.editSelectAll()

    def editSlide(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        self._editMove(items, pos, True)

    def editMove(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        self._editMove(items, pos, False)

    def editResize(
        self : "DrawingViewUi",
        grip : "ResizeGripItem",
        pos  : QPoint | QPointF | None = None
    ) -> None:
        pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(self._view, [grip], pos)
        self._view.state.go(self._view.stateEditResize)

    def editRotateCW(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self._view.interaction:  # interaction in progress
            if isinstance(self._view.interaction, RotateItemMixin):
                self._view.interaction.rotateCW()
        else:
            if items is None:
                items = self._scene.selectedItems()
            pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
            self._scene.editRotateCW(items, pos, undoable=True)

    def editRotateCCW(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self._view.interaction:  # interaction in progress
            if isinstance(self._view.interaction, RotateItemMixin):
                self._view.interaction.rotateCCW()
        else:
            if items is None:
                items = self._scene.selectedItems()
            pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
            self._scene.editRotateCCW(items, pos, undoable=True)

    def editAssignOrigin(
        self    : "DrawingViewUi",
        item    : "ItemMixin",
        ap_name : str
    ) -> None:
        self._scene.editAssignOrigin(item, ap_name, undoable=True)

    def editAppearance(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditAppearance, [item] if item else None)

    def editItemProperties(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditItemProperties, [item] if item else None)

    def editDrawingProperties(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditDrawingProperties)

    def editQuery(self : "DrawingViewUi", vpos : QPoint | None = None) -> None:
        if vpos is None:
            initial_items = self._scene.selectedItems()
            items = []
            # add (unselected) children
            def _addChildren(item : QGraphicsItem) -> None:
                if item in items:
                    return
                items.append(item)
                for child in item.childItems():
                    _addChildren(child)
            for item in initial_items:
                _addChildren(item)
        else:
            items = self._view._itemsAt(vpos)
        query_window = QueryWindow(items)
        if not hasattr(self, '_query_windows'):
            self._query_windows = []
        self._query_windows.append(query_window)
        query_window.adjustSize()
        mouse_pos = QCursor.pos()
        window_size = query_window.size()
        window_width = window_size.width()
        window_height = window_size.height()
        final_x = mouse_pos.x() - window_width // 2
        final_y = mouse_pos.y() - window_height // 2
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        final_x = max(0, min(final_x, screen_width - window_width))
        final_y = max(0, min(final_y, screen_height - window_height))
        query_window.move(final_x, final_y)
        query_window.show()
        query_window.raise_()
        query_window.activateWindow()
        def cleanup():
            if query_window in self._query_windows:
                self._query_windows.remove(query_window)
        query_window.destroyed.connect(cleanup)

    def editPort(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditPort, [item] if item else None)

    def editBlockPin(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditBlockPin, [item] if item else None)

    def editSymbolPinDot(
        self   : "DrawingViewUi",
        item   : "SymbolPinItem",
        enable : bool
    ):
        if enable == item.dot():
            return
        self._scene.editSymbolPinDot(item, enable, undoable=True)

    def editSymbolPinClock(
        self   : "DrawingViewUi",
        item   : "SymbolPinItem",
        enable : bool
    ):
        if enable == item.clock():
            return
        self._scene.editSymbolPinClock(item, enable, undoable=True)

    def editTextDialog(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditText)

    def editText(
        self      : "DrawingViewUi",
        item      : "TextItem",
        origin    : str          | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float        | NoChange = NO_CHANGE,
        height    : float        | NoChange = NO_CHANGE,
    ) -> None:
        self._scene.editText(
            item     = item,
            origin   = origin,
            align_h  = align_h,
            align_v  = align_v,
            width    = width,
            height   = height,
            undoable = True
        )

    def editPropertyTextDialog(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(
            self._view.stateEditPropertyText, [item] if item else None
        )

    def _editMove(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None,
        slide : bool = False
    ) -> None:
        from ....items import ItemMixin
        if items is None:
            items = self._scene.selectedItems()
        pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
        # exclude: non-items and child items
        for item in items:
            if not isinstance(item, ItemMixin) \
            or item.topParentItem() in items:
                items.remove(item)
        # slide/move
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(self._view, items, pos, slide)
        self._view.state.go(
            self._view.stateEditSlide if slide else self._view.stateEditMove
        )
