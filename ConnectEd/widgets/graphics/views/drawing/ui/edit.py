from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui     import QCursor

from ....query import QueryWindow

from ..interaction      import RotateMixin
from ..interaction.edit import EditMoveInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing     import DrawingScene
    from ....items              import ItemMixin
    from ....items.anchor_point import AnchorPoint
    from ....items.handle       import ResizeGrip
    from .                      import DrawingViewUi


class DrawingViewUiEditMixin:
    def editUndo(self : "DrawingViewUi") -> None:
        self.scene().undo()

    def editRedo(self : "DrawingViewUi") -> None:
        self.scene().redo()

    def editRepeat(self : "DrawingViewUi") -> None:
        raise NotImplementedError("editRepeat not implemented")

    def editCancel(self : "DrawingViewUi") -> None:
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = None
        self._view.scene().clearSelection()
        self._view.state.go(self._view.stateIdle)

    def editCut(self : "DrawingViewUi") -> None:
        self._view.scene().editCut(self._snap(self._view.mouse.current.logical))

    def editCopy(self : "DrawingViewUi") -> None:
        self._view.scene().editCopy(self._snap(self._view.mouse.current.logical))

    def editPaste(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditPaste)

    def editDelete(self : "DrawingViewUi") -> None:
        scene : "DrawingScene" = self._view.scene()
        scene.editDelete()

    def editDuplicate(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditDuplicate)

    def editSelectArea(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditSelectArea1)

    def editSelectAll(self : "DrawingViewUi") -> None:
        self._view.scene().editSelectAll()

    def editSlide(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        scene : "DrawingScene" = self._view.scene()
        if items is None:
            items = scene.selectedItems()
        pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(scene, items, pos, True)
        self._view.state.go(self._view.stateEditSlide)

    def editMove(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        scene : "DrawingScene" = self._view.scene()
        if items is None:
            items = scene.selectedItems()
        pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(scene, items, pos, False)
        self._view.state.go(self._view.stateEditMove)

    def editResize(
        self : "DrawingViewUi",
        grip : "ResizeGrip",
        pos  : QPoint | QPointF | None = None
    ) -> None:
        scene : "DrawingScene" = self._view.scene()
        pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(scene, [grip], pos)
        self._view.state.go(self._view.stateEditResize)

    def editRotateCW(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self._view.interaction:  # interaction in progress
            if isinstance(self._view.interaction, RotateMixin):
                self._view.interaction.rotateCW()
        else:
            scene : "DrawingScene" = self._view.scene()
            if items is None:
                items = scene.selectedItems()
            pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
            # TODO push command

    def editRotateCCW(
        self  : "DrawingViewUi",
        items : list["ItemMixin"] | None = None,
        pos   : QPoint | QPointF | None = None
    ) -> None:
        if self._view.interaction:  # interaction in progress
            if isinstance(self._view.interaction, RotateMixin):
                self._view.interaction.rotateCCW()
        else:
            scene : "DrawingScene" = self._view.scene()
            if items is None:
                items = scene.selectedItems()
            pos = self._view.mapToScene(pos) if isinstance(pos, QPoint) else pos
            # TODO push command

    def editAssignOrigin(self : "DrawingViewUi", ap : "AnchorPoint") -> None:
        from ....scenes.drawing.cmd.edit import CmdEditOrigin
        scene  : "DrawingScene" = self._view.scene()
        scene.undo_stack.push(CmdEditOrigin(scene, ap))

    def editAppearance(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditAppearance, [item] if item else None)

    def editProperties(
        self : "DrawingViewUi",
        item : "ItemMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditProperties, [item] if item else None)

    def editQuery(self : "DrawingViewUi", vpos : QPoint | None = None) -> None:
        if vpos is None:
            initial_items = self._view.scene().selectedItems()
            items = []
            print("items", items)
            # add (unselected) children
            def _addChildren(item : QGraphicsItem) -> None:
                if item in items:
                    return
                items.append(item)
                for child in item.childItems():
                    _addChildren(child)
            for item in initial_items:
                _addChildren(item)
            print("items", items)
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
        self._view.state.go(
            self._view.stateEditBlockPin, [item] if item else None
        )

    def editText(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditText)

    def editPropertyText(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditPropertyText)
