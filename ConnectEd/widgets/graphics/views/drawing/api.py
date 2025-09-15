from typing import Self, Optional

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QCursor

from .....app import settings

from ...query  import QueryWindow

from ...scenes.drawing import DrawingScene

from ...items import ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..drawing import DrawingView


def withScene(func):
    def wrapper(self : Self, *args, **kwargs):
        return func(self, *args, **kwargs, scene=self.scene())
    return wrapper

class DrawingViewApiMixin:

    ############################################################################
    # edit menu and associated context menus
    ############################################################################

    @withScene
    def editUndo(self : "DrawingView", scene : DrawingScene) -> None:
        scene.undo()

    @withScene
    def editRedo(self : "DrawingView", scene : DrawingScene) -> None:
        scene.redo()

    # TODO: editRepeat

    @withScene
    def editCancel(self : "DrawingView", scene : DrawingScene) -> None:
        if self.interaction:
            self.interaction.cancel()
        self.interaction = None
        scene.clearSelection()
        self.state.go(self.stateIdle)

    @withScene
    def editCut(self : "DrawingView", scene : DrawingScene) -> None:
        scene.editCut(self._snap(self.mouse.current.logical))

    @withScene
    def editCopy(self : "DrawingView", scene : DrawingScene) -> None:
        scene.editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : "DrawingView") -> None:
        self.state.go(self.stateEditPaste)

    @withScene
    def editDelete(self : "DrawingView", scene : DrawingScene) -> None:
        scene.editDelete()

    def editDuplicate(self : "DrawingView") -> None:
        self.state.go(self.stateEditDuplicate)

    def editSelectArea(self : "DrawingView") -> None:
        self.state.go(self.stateEditSelectArea1)

    @withScene
    def editSelectAll(self : "DrawingView", scene : DrawingScene) -> None:
        scene.editSelectAll()

    def editAppearance(
        self    : "DrawingView",
        element : Optional[ElementMixin] = None
    ) -> None:
        self.state.go(self.stateEditAppearance, [element] if element else None)

    def editProperties(
        self    : "DrawingView",
        element : Optional[ElementMixin] = None
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

    ############################################################################
    # edit context menus
    ############################################################################

    def editPort(
        self    : "DrawingView",
        element : Optional[ElementMixin] = None
    ) -> None:
        self.state.go(self.stateEditPort, [element] if element else None)

    def editBlockPin(
        self    : "DrawingView",
        element : Optional[ElementMixin] = None
    ) -> None:
        self.state.go(self.stateEditBlockPin, [element] if element else None)

    def editText(self : "DrawingView") -> None:
        self.state.go(self.stateEditText)

    def editPropertyText(self : "DrawingView") -> None:
        self.state.go(self.stateEditPropertyText)

    ############################################################################
    # view menu
    ############################################################################

    def viewZoomAll(self : "DrawingView") -> None:
        rect = self._allItemsRect()
        if rect is None:
            self._zoomAbs(1)
        else:
            self._zoomRect(rect)

    def viewZoomArea(self : "DrawingView") -> None:
        self.state.go(self.stateViewZoomArea1)

    def viewZoomIn(self : "DrawingView", n : int = 1) -> None:
        self._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    def viewZoomOut(self : "DrawingView", n : int = 1) -> None:
        self._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    def viewPan(self : "DrawingView", n : int = 1) -> None:
        self.state.go(self.stateViewPan1)

    def viewPanLeft(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(settings().get("display/pan/step") * n, 0))

    def viewPanRight(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    def viewPanUp(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(0, settings().get("display/pan/step") * n))

    def viewPanDown(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(0, -settings().get("display/pan/step") * n))

    def viewPrev(self : "DrawingView") -> None:
        pass

    def viewNext(self : "DrawingView") -> None:
        pass

    def viewGridDisplay(self : "DrawingView", checked : bool) -> None:
        self.grid.display = checked
        self.viewport().update()

    def viewGridSnap(self : "DrawingView", checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : "DrawingView") -> None:
        # TODO dialog required
        pass

    ############################################################################
    # place menu
    ############################################################################

    def placePort(self : "DrawingView") -> None:
        self.state.go(self.statePlacePort)

    def placeBlock(self : "DrawingView") -> None:
        self.state.go(self.statePlaceBlock1)

    def placeBlockPin(self : "DrawingView") -> None:
        self.state.go(self.statePlaceBlockPin)

    def placeRectangle(self : "DrawingView") -> None:
        self.state.go(self.statePlaceRectangle1)

    def placeTextBlock(self : "DrawingView") -> None:
        self.state.go(self.statePlaceTextBlock)

    def placeText(self : "DrawingView") -> None:
        self.state.go(self.statePlaceText)
