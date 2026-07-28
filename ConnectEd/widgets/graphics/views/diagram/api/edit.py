from __future__ import annotations

from typing          import Self
from collections.abc import Sequence

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui     import QCursor

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                             HandleId, RectHandleId

from ....query import QueryWindow

from ....scenes import withScene

from ....items.port      import PortItem
from ....items.block_pin import BlockPinItem

from ....items.mixin     import ItemMixin

from ..interaction      import RotateItemMixin
from ..interaction.edit import EditMoveInteraction

from ..host import asDiagramView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram   import DiagramScene
    from ....items.text       import TextItem
    from ....items.grip       import ResizeGripItem
    from ....items.port_pin   import PortPinPathItem
    from ....items.symbol_pin import SymbolPinItem


class DiagramViewApiEditMixin:
    _query_windows : list[QueryWindow]

    @withScene
    @checked
    def editUndo(self : Self, scene : DiagramScene) -> None:
        scene.undo()

    @withScene
    @checked
    def editRedo(self : Self, scene : DiagramScene) -> None:
        scene.redo()

    @withScene
    @checked
    def editRepeat(self : Self) -> None:
        raise NotImplementedError("editRepeat not implemented")

    @withScene
    @checked
    def editCancel(self : Self, scene : DiagramScene) -> None:
        host = asDiagramView(self)
        scene.clearSelection()
        host.state.go(host.stateIdle)

    @withScene
    @checked
    def editCut(self : Self, scene : DiagramScene) -> None:
        host = asDiagramView(self)
        scene.editCut(host._snap(host._mouse_spos), undoable=True)

    @withScene
    @checked
    def editCopy(self : Self, scene : DiagramScene) -> None:
        host = asDiagramView(self)
        scene.editCopy(host._snap(host._mouse_spos))

    @checked
    def editPaste(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditPaste)

    @withScene
    @checked
    def editDelete(self : Self, scene : DiagramScene) -> None:
        scene.editDelete(undoable=True)

    @checked
    def editDuplicate(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditDuplicate)

    @checked
    def editSelectArea(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditSelectArea1)

    @withScene
    @checked
    def editSelectAll(self : Self, scene : DiagramScene) -> None:
        scene.editSelectAll()

    @checked
    def editSlide(
        self  : Self,
        items : Sequence[QGraphicsItem],
        pos   : QPoint | QPointF | None = None
    ) -> None:
        host = asDiagramView(self)
        host._editMove(items, pos, True)

    @checked
    def editMove(
        self  : Self,
        items : Sequence[QGraphicsItem],
        pos   : QPointF
    ) -> None:
        host = asDiagramView(self)
        host._editMove(items, pos, False)

    @checked
    def editResize(
        self : Self,
        grip : ResizeGripItem,
        pos  : QPointF
    ) -> None:
        host = asDiagramView(self)
        pos = host.mapToScene(pos) if isinstance(pos, QPoint) else pos
        host.state.interact(
            EditMoveInteraction(host, [grip], pos), host.stateEditResize
        )

    @withScene
    @checked
    def editRotateCW(
        self  : Self,
        scene : DiagramScene,
        items : QGraphicsItem | list[QGraphicsItem] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        host = asDiagramView(self)
        if host.interaction:  # interaction in progress
            if isinstance(host.interaction, RotateItemMixin):
                host.interaction.rotateCW()
        else:
            if items is None:
                items = scene.selectedItems()
            elif not isinstance(items, list):
                items = [items]
            pos = host.mapToScene(pos) if isinstance(pos, QPoint) else pos
            scene.editRotateCW(items, pos, undoable=True)

    @withScene
    @checked
    def editRotateCCW(
        self  : Self,
        scene : DiagramScene,
        items : QGraphicsItem | list[QGraphicsItem] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        host = asDiagramView(self)
        if host.interaction:  # interaction in progress
            if isinstance(host.interaction, RotateItemMixin):
                host.interaction.rotateCCW()
        else:
            if items is None:
                items = scene.selectedItems()
            elif not isinstance(items, list):
                items = [items]
            pos = host.mapToScene(pos) if isinstance(pos, QPoint) else pos
            scene.editRotateCCW(items, pos, undoable=True)

    @withScene
    @checked
    def editAssignOrigin(
        self    : Self,
        scene   : DiagramScene,
        item    : QGraphicsItem,
        handle  : HandleId
    ) -> None:
        scene.editAssignOrigin(item, handle, undoable=True)

    @checked
    def editAppearance(
        self  : Self,
        items : QGraphicsItem | Sequence[QGraphicsItem] | None = None
    ) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditAppearance, items)

    @checked
    def editItemProperties(
        self  : Self,
        items : QGraphicsItem | Sequence[QGraphicsItem] | None = None
    ) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditItemProperties, items)

    @checked
    def editDiagramProperties(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditDiagramProperties)

    @withScene
    @checked
    def editQuery(
        self  : Self,
        scene : DiagramScene,
        vpos  : QPoint | None = None
    ) -> None:
        host = asDiagramView(self)
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
            items = host._itemsAt(vpos)
        query_window = QueryWindow(items)
        if not hasattr(host, '_query_windows'):
            host._query_windows = []
        host._query_windows.append(query_window)
        query_window.adjustSize()
        mouse_pos = QCursor.pos()
        window_size = query_window.size()
        window_width = window_size.width()
        window_height = window_size.height()
        final_x = mouse_pos.x() - window_width // 2
        final_y = mouse_pos.y() - window_height // 2
        if (primary_screen := QApplication.primaryScreen()) is None:
            raise ValueError("Primary screen is None")
        screen = primary_screen.availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        final_x = max(0, min(final_x, screen_width - window_width))
        final_y = max(0, min(final_y, screen_height - window_height))
        query_window.move(final_x, final_y)
        query_window.show()
        query_window.raise_()
        query_window.activateWindow()
        def cleanup():
            if query_window in host._query_windows:
                host._query_windows.remove(query_window)
        query_window.destroyed.connect(cleanup)

    @checked
    def editPort(
        self : Self,
        item : PortItem
    ) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditPort, [item])

    @checked
    def editBlockPin(
        self : Self,
        item : BlockPinItem
    ) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditBlockPin, [item])

    @withScene
    @checked
    def editPinDot(
        self   : Self,
        scene  : DiagramScene,
        item   : PortPinPathItem,
        enable : bool
    ) -> None:
        if enable == item.dot():
            return
        scene.editPinDot(item, enable, undoable=True)

    @withScene
    @checked
    def editPinClk(
        self   : Self,
        scene  : DiagramScene,
        item   : SymbolPinItem,
        enable : bool
    ) -> None:
        if enable == item.clock():
            return
        scene.editPinClk(item, enable, undoable=True)

    @checked
    def editTextDialog(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditText)

    @withScene
    @checked
    def editText(
        self      : Self,
        scene     : DiagramScene,
        item      : TextItem,
        mirror_h  : bool         | NoChange = NO_CHANGE,
        mirror_v  : bool         | NoChange = NO_CHANGE,
        origin    : RectHandleId | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float        | NoChange = NO_CHANGE,
        height    : float        | NoChange = NO_CHANGE,
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

    @checked
    def editPropertyTextDialog(
        self : Self,
        item : QGraphicsItem
    ) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateEditPropertyText, [item])

    @withScene
    @checked
    def _editMove(
        self  : Self,
        scene : DiagramScene,
        items : QGraphicsItem | list[QGraphicsItem],
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        host = asDiagramView(self)
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if isinstance(item, ItemMixin) and item.topParentItem() in items:
                items.remove(item)
        # slide/move
        host.state.interact(
            EditMoveInteraction(host, items, pos, slide),
            host.stateEditSlide if slide else host.stateEditMove
        )
