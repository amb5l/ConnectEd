from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui     import QCursor

from ....query import QueryWindow

from ..interaction.edit import EditMoveInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from ....items import ElementMixin
    from ....items.anchor_point import AnchorPoint
    from . import DrawingViewUi


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
        self.scene().editDelete()

    def editDuplicate(self : "DrawingViewUi") -> None:
        self.state.go(self.stateEditDuplicate)

    def editSelectArea(self : "DrawingViewUi") -> None:
        self.state.go(self.stateEditSelectArea1)

    def editSelectAll(self : "DrawingViewUi") -> None:
        self._view.scene().editSelectAll()

    def editSlide(
        self     : "DrawingViewUi",
        elements : list["ElementMixin"] | None = None,
        pos      : QPointF | None = None
    ) -> None:
        scene : "DrawingScene" = self._view.scene()
        if elements is None:
            elements = scene.selectedItems()
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(scene, elements, pos, True)
        self._view.state.go(self._view.stateEditSlide)

    def editMove(
        self     : "DrawingViewUi",
        elements : list["ElementMixin"] | None = None,
        pos      : QPointF | None = None
    ) -> None:
        scene : "DrawingScene" = self._view.scene()
        if elements is None:
            elements = scene.selectedItems()
        if self._view.interaction:
            self._view.interaction.cancel()
        self._view.interaction = EditMoveInteraction(scene, elements, pos, False)
        self._view.state.go(self._view.stateEditMove)

    def editResize(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditResize)

    def editAssignOrigin(self : "DrawingViewUi", element : "QGraphicsItem") -> None:
        from ....scenes.drawing.cmd.edit import cmdEditOrigin
        scene  : "DrawingScene" = self._view.scene()
        parent : "AnchorPoint" = element.parentItem()
        scene.undo_stack.push(cmdEditOrigin(
            scene,
            self._element, # element
            parent.name()  # name of anchor point
        ))

    def editAppearance(
        self    : "DrawingViewUi",
        element : "ElementMixin | None" = None
    ) -> None:
        self._view.state.go(self.stateEditAppearance, [element] if element else None)

    def editProperties(
        self    : "DrawingViewUi",
        element : "ElementMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditProperties, [element] if element else None)

    def editQuery(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditQuery)
        items_at = self._itemsAt(self.mouse.current.logical)
        if items_at:
            element = items_at[0]
        elif len(self.scene().selectedItems()) == 1:
            element = self.scene().selectedItems()[0]
        else:
            return
        query_window = QueryWindow(element)
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
        self.state.go(self.stateIdle)

    def editPort(
        self    : "DrawingViewUi",
        element : "ElementMixin | None" = None
    ) -> None:
        self._view.state.go(self._view.stateEditPort, [element] if element else None)

    def editBlockPin(
        self    : "DrawingViewUi",
        element : "ElementMixin | None" = None
    ) -> None:
        self._view.state.go(
            self._view.stateEditBlockPin, [element] if element else None
        )

    def editText(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditText)

    def editPropertyText(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.stateEditPropertyText)
