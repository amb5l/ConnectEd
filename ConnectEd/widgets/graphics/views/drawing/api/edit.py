from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui     import QCursor

from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV

from ....query import QueryWindow

from ....scenes import withScene

from ..interaction      import RotateItemMixin
from ..interaction.edit import EditMoveInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing   import DrawingScene
    from ....items.mixin      import ItemMixin
    from ....items.text       import TextItem
    from ....items.grip       import ResizeGripItem
    from ....items.symbol_pin import SymbolPinItem
    from .. import DrawingView
    MixinSelf: TypeAlias = Self | DrawingView
else:
    MixinSelf = Self


class DrawingViewApiEditMixin:
    @withScene
    def editUndo(self : MixinSelf, scene : DrawingScene) -> None:
        scene.undo()

    @withScene
    def editRedo(self : MixinSelf, scene : DrawingScene) -> None:
        scene.redo()

    @withScene
    def editRepeat(self : MixinSelf) -> None:
        raise NotImplementedError("editRepeat not implemented")

    @withScene
    def editCancel(self : MixinSelf, scene : DrawingScene) -> None:
        scene.clearSelection()
        self.state.go(self.stateIdle)

    @withScene
    def editCut(self : MixinSelf, scene : DrawingScene) -> None:
        scene.editCut(
            self._snap(self.mouse.current.logical), undoable=True
        )

    @withScene
    def editCopy(self : MixinSelf, scene : DrawingScene) -> None:
        scene.editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : MixinSelf) -> None:
        self.state.go(self.stateEditPaste)

    @withScene
    def editDelete(self : MixinSelf, scene : DrawingScene) -> None:
        scene.editDelete(undoable=True)

    def editDuplicate(self : MixinSelf) -> None:
        self.state.go(self.stateEditDuplicate)

    def editSelectArea(self : MixinSelf) -> None:
        self.state.go(self.stateEditSelectArea1)

    @withScene
    def editSelectAll(self : MixinSelf, scene : DrawingScene) -> None:
        scene.editSelectAll()

    def editSlide(
        self  : MixinSelf,
        items : list[ItemMixin] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        self._editMove(items, pos, True)

    def editMove(
        self  : MixinSelf,
        items : list[ItemMixin] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        self._editMove(items, pos, False)

    def editResize(
        self : MixinSelf,
        grip : ResizeGripItem,
        pos  : QPoint | QPointF | None = None
    ) -> None:
        pos = self.mapToScene(pos) if isinstance(pos, QPoint) else pos
        self.state.interact(
            EditMoveInteraction(self._view, [grip], pos),
            self.stateEditResize
        )

    @withScene
    def editRotateCW(
        self  : MixinSelf,
        scene : DrawingScene,
        items : list[ItemMixin] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self.interaction:  # interaction in progress
            if isinstance(self.interaction, RotateItemMixin):
                self.interaction.rotateCW()
        else:
            if items is None:
                items = scene.selectedItems()
            pos = self.mapToScene(pos) if isinstance(pos, QPoint) else pos
            scene.editRotateCW(items, pos, undoable=True)

    @withScene
    def editRotateCCW(
        self  : MixinSelf,
        scene : DrawingScene,
        items : list[ItemMixin] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self.interaction:  # interaction in progress
            if isinstance(self.interaction, RotateItemMixin):
                self.interaction.rotateCCW()
        else:
            if items is None:
                items = scene.selectedItems()
            pos = self.mapToScene(pos) if isinstance(pos, QPoint) else pos
            scene.editRotateCCW(items, pos, undoable=True)

    @withScene
    def editAssignOrigin(
        self    : MixinSelf,
        scene   : DrawingScene,
        item    : ItemMixin,
        ap_name : str
    ) -> None:
        scene.editAssignOrigin(item, ap_name, undoable=True)

    def editAppearance(
        self  : MixinSelf,
        items : ItemMixin | list[ItemMixin] | None = None
    ) -> None:
        from ....items.mixin import ItemMixin
        items = [items] if isinstance(items, ItemMixin) else items
        self.state.go(self.stateEditAppearance, items)

    def editItemProperties(
        self  : MixinSelf,
        items : ItemMixin | list[ItemMixin] | None = None
    ) -> None:
        from ....items.mixin import ItemMixin
        items = [items] if isinstance(items, ItemMixin) else items
        self.state.go(self.stateEditItemProperties, items)

    def editDrawingProperties(self : MixinSelf) -> None:
        self.state.go(self.stateEditDrawingProperties)

    @withScene
    def editQuery(
        self  : MixinSelf,
        scene : DrawingScene,
        vpos  : QPoint | None = None
    ) -> None:
        if vpos is None:
            initial_items = scene.selectedItems()
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
            items = self._itemsAt(vpos)
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
        self : MixinSelf,
        item : ItemMixin | None = None
    ) -> None:
        self.state.go(self.stateEditPort, [item] if item else None)

    def editBlockPin(
        self : MixinSelf,
        item : ItemMixin | None = None
    ) -> None:
        self.state.go(self.stateEditBlockPin, [item] if item else None)

    @withScene
    def editSymbolPinDot(
        self   : MixinSelf,
        scene  : DrawingScene,
        item   : SymbolPinItem,
        enable : bool
    ):
        if enable == item.dot():
            return
        scene.editSymbolPinDot(item, enable, undoable=True)

    @withScene
    def editSymbolPinClock(
        self   : MixinSelf,
        scene  : DrawingScene,
        item   : SymbolPinItem,
        enable : bool
    ):
        if enable == item.clock():
            return
        scene.editSymbolPinClock(item, enable, undoable=True)

    def editTextDialog(self : MixinSelf) -> None:
        self.state.go(self.stateEditText)

    @withScene
    def editText(
        self      : MixinSelf,
        scene     : DrawingScene,
        item      : TextItem,
        mirror_h  : bool   | NoChange = NO_CHANGE,
        mirror_v  : bool   | NoChange = NO_CHANGE,
        origin    : str    | NoChange = NO_CHANGE,
        align_h   : AlignH | NoChange = NO_CHANGE,
        align_v   : AlignV | NoChange = NO_CHANGE,
        width     : float  | NoChange = NO_CHANGE,
        height    : float  | NoChange = NO_CHANGE,
    ) -> None:
        scene.editText(
            item     = item,
            mirror_h = mirror_h,
            mirror_v = mirror_v,
            origin   = origin,
            align_h  = align_h,
            align_v  = align_v,
            width    = width,
            height   = height,
            undoable = True
        )

    def editPropertyTextDialog(
        self : MixinSelf,
        item : ItemMixin | None = None
    ) -> None:
        self.state.go(
            self.stateEditPropertyText, [item] if item else None
        )

    @withScene
    def _editMove(
        self  : MixinSelf,
        scene : DrawingScene,
        items : list[ItemMixin] | None = None,
        pos   : QPoint | QPointF | None = None,
        slide : bool = False
    ) -> None:
        from ....items.mixin import ItemMixin
        if items is None:
            items = scene.selectedItems()
        pos = self.mapToScene(pos) if isinstance(pos, QPoint) else pos
        # exclude: non-items and child items
        for item in items:
            if not isinstance(item, ItemMixin) \
            or item.topParentItem() in items:
                items.remove(item)
        # slide/move
        self.state.interact(
            EditMoveInteraction(self._view, items, pos, slide),
            self.stateEditSlide if slide else self.stateEditMove
        )
