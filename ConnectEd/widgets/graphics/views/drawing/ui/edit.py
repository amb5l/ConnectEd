from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QCursor

from ....query import QueryWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from ....items import ElementMixin
    from ....items.anchor_point import AnchorPoint
    from .. import DrawingView


class DrawingViewUiEditMixin:
    def editUndo(self : "DrawingView") -> None:
        self.scene().undo()

    def editRedo(self : "DrawingView") -> None:
        self.scene().redo()

    def editRepeat(self : "DrawingView") -> None:
        raise NotImplementedError("editRepeat not implemented")

    def editCancel(self : "DrawingView") -> None:
        if self.interaction:
            self.interaction.cancel()
        self.interaction = None
        self.scene().clearSelection()
        self.state.go(self.stateIdle)

    def editCut(self : "DrawingView") -> None:
        self.scene().editCut(self._snap(self.mouse.current.logical))

    def editCopy(self : "DrawingView") -> None:
        self.scene().editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : "DrawingView") -> None:
        self.state.go(self.stateEditPaste)

    def editDelete(self : "DrawingView") -> None:
        self.scene().editDelete()

    def editDuplicate(self : "DrawingView") -> None:
        self.state.go(self.stateEditDuplicate)

    def editSelectArea(self : "DrawingView") -> None:
        self.state.go(self.stateEditSelectArea1)

    def editSelectAll(self : "DrawingView") -> None:
        self.scene().editSelectAll()

    def editSlide(self : "DrawingView") -> None:
        self.state.go(self.stateEditSlide)

    def editMove(self : "DrawingView") -> None:
        self.state.go(self.stateEditMove)

    def editResize(self : "DrawingView") -> None:
        self.state.go(self.stateEditResize)

    def editAssignOrigin(self : "DrawingView", element : "ElementMixin") -> None:
        self.state.go(self.stateEditAssignOrigin, [element])
        from ....scenes.drawing.cmd.edit import cmdEditOrigin
        scene  : "DrawingScene" = self.scene()
        parent : "AnchorPoint" = self.parentItem()
        scene.undo_stack.push(cmdEditOrigin(
            scene,
            self._element, # element
            parent.name()  # name of anchor point
        ))

    def editAppearance(
        self    : "DrawingView",
        element : "ElementMixin | None" = None
    ) -> None:
        self.state.go(self.stateEditAppearance, [element] if element else None)

    def editProperties(
        self    : "DrawingView",
        element : "ElementMixin | None" = None
    ) -> None:
        self.state.go(self.stateEditProperties, [element] if element else None)

    def editQuery(self : "DrawingView") -> None:
        self.state.go(self.stateEditQuery)
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
        self    : "DrawingView",
        element : "ElementMixin | None" = None
    ) -> None:
        self.state.go(self.stateEditPort, [element] if element else None)

    def editBlockPin(
        self    : "DrawingView",
        element : "ElementMixin | None" = None
    ) -> None:
        self.state.go(self.stateEditBlockPin, [element] if element else None)

    def editText(self : "DrawingView") -> None:
        self.state.go(self.stateEditText)

    def editPropertyText(self : "DrawingView") -> None:
        self.state.go(self.stateEditPropertyText)
