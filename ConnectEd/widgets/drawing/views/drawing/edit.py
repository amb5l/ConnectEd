from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QCursor

from .....core import logger, paste

from ....dialogs import TextDialog, AppearanceDialog, \
                        PropertiesDialog, PropertyTextDialog

from ...scenes import DrawingScene
from ...items  import ElementMixin, AnchorPoint, PropertyText
from ...query  import QueryWindow

from ...scenes.api.operation import OpType
from ...items.base_text import BaseText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ... import DrawingView


class DrawingViewEditMixin:
    def editUndo(self : "DrawingView") -> None:
        self.scene().undo_stack.undo()

    def editRedo(self : "DrawingView") -> None:
        self.scene().undo_stack.redo()

    def editCancel(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if self.wip.macro:
            scene.undo_stack.endMacro()
        scene.undo_stack.undo()
        self.wip.clear()
        self.scene().clearSelection()
        self.state.go(self.stateIdle)

    def editComplete(self : "DrawingView") -> None:
        # TODO seriously consider this
        match self.state:
            case self.statePlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.current.logical)
                )

    def editSelectAll(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editSelectAll()

    def editSelectArea(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editSelectArea()

    def editDeselectAll(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editDeselectAll()

    def editCut(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editCut(self._snap(self.mouse.current.logical))

    def editCopy(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : "DrawingView") -> None:
        self._beginOperation(OpType.PASTE, self.stateEditPaste)

    def editPasteContinue(self : "DrawingView") -> None:
        self._continueOperation()

    def editPasteComplete(self : "DrawingView") -> None:
        self._completeOperation()

    def editDelete(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editDelete()

    def editDuplicate(self : "DrawingView", pos: QPointF = None) -> None:
        elements = [item for item in self.scene().selectedItems() 
                   if isinstance(item, ElementMixin)]
        params = OperationParams(elements=elements)
        self._beginOperation(OperationType.DUPLICATE, self.stateEditDuplicate2, params)

    def editDuplicateContinue(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editDuplicateContinue: No elements in wip, aborting")
            self.state.go(self.stateIdle)
            return
        new_pos = self._snap(self.mouse.current.logical)
        mouse_delta = new_pos - self.wip.pos
        # Block signals to avoid multiple selection updates
        scene.blockSignals(True)
        for element in self.wip.elements:
            if element.scene() == scene:
                element.setPos(element.pos() + mouse_delta)
                element.setSelected(True)  # Ensure elements remain selected
        scene.blockSignals(False)
        # Manually trigger selection changed to update anchor points
        scene.selectionChanged.emit()
        self.wip.pos = new_pos

    def editDuplicateComplete(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editDuplicateComplete: No elements in wip, aborting")
            self.state.go(self.stateIdle)
            return
        pos = self._snap(self.mouse.current.logical)
        offset = pos - self.wip.pos
        # Remove temporary elements from scene before final placement
        for element in self.wip.elements:
            if element.scene() == scene:
                scene.removeItem(element)
                element.setPos(element.pos() - offset)
        # Use the original selection to determine what was duplicated
        original_elements = self.wip.selection if self.wip.selection else []
        # Pass the cloned elements to editDuplicate for final placement
        scene.editDuplicate(pos, (self.wip.elements, self.wip.pos, original_elements))
        if self.wip.macro:
            scene.undo_stack.endMacro()
        self.wip.clear()
        self.state.go(self.stateIdle)

    def editSlide(self : "DrawingView") -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.editMoveBegin(self.scene().selectedItems(), pos, True)
        else:
            self.state.go(self.stateEditSlide1)

    def editMove(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if scene.selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.editMoveBegin(scene.selectedItems(), pos)
            self.state.go(self.stateEditMove2)
        else:
            self.state.go(self.stateEditMove1)

    def editMoveBegin(
        self     : "DrawingView",
        elements : list[ElementMixin],
        pos      : QPointF,
        slide    : bool = False
    ) -> None:
        scene : DrawingScene = self.scene()
        scene.undo_stack.beginMacro("Move Elements")
        self.wip.elements = elements
        if isinstance(elements[0], AnchorPoint):
            pos = elements[0].scenePos()
        self.wip.pos = pos
        self.wip.pos0 = pos
        self.wip.slide = slide

    def editMoveContinue(
        self  : "DrawingView",
        pos   : QPointF,
        ortho : bool = False
    ) -> None:
        scene : DrawingScene = self.scene()
        if ortho:
            pos0 = self.wip.pos0
            if abs(pos.x() - pos0.x()) > abs(pos.y() - pos0.y()):
                pos.setY(pos0.y())
            else:
                pos.setX(pos0.x())
        scene.editMove(self.wip.elements, pos - self.wip.pos, self.wip.slide)
        self.wip.pos = pos

    def editMoveComplete(
        self  : "DrawingView",
        pos   : QPointF,
        ortho : bool = False
    ) -> None:
        scene : DrawingScene = self.scene()
        if ortho:
            pos0 = self.wip.pos0
            if abs(pos.x() - pos0.x()) > abs(pos.y() - pos0.y()):
                pos.setY(pos0.y())
            else:
                pos.setX(pos0.x())
        scene.editMove(self.wip.elements, pos - self.wip.pos, self.wip.slide)
        scene.undo_stack.endMacro()
        self.wip.clear()

    def editResize(self : "DrawingView") -> None:
        if len(self.scene().selectedItems()) == 1:
            self.state.go(self.stateEditResize2)
        else:
            self.scene().clearSelection()
            self.state.go(self.stateEditResize1)

    def editText(self : "DrawingView", element: BaseText) -> None:
        self.state.go(self.stateIdle) # TODO have state/tip for dialog
        scene : DrawingScene = self.scene()
        dialog = TextDialog(element)
        if dialog.exec():
            scene.editText(element, *dialog.getChoice())

    def editPropertyText(self : "DrawingView", element: PropertyText) -> None:
        self.state.go(self.stateIdle) # TODO have state/tip for dialog
        scene : DrawingScene = self.scene()
        dialog = PropertyTextDialog(element)
        if dialog.exec():
            scene.editPropertyText(
                element,
                dialog.getName(),
                dialog.getValue(),
                dialog.getAppearanceChange()
            )

    def editAppearance(
        self : "DrawingView",
        elements : ElementMixin | list[ElementMixin] = []
    ) -> None:
        scene : DrawingScene = self.scene()
        if scene.selectedItems():
            elements = scene.selectedItems()
        elif not isinstance(elements, list):
            elements = [elements]
        if elements:
            self.state.go(self.stateEditAppearance2)
            dialog = AppearanceDialog(elements)
            if dialog.exec():
                scene.editAppearance(
                    elements,
                    dialog.getChoice()
                )
            self.state.go(self.stateIdle)
        else:
            self.state.go(self.stateEditAppearance1)

    def editProperties(self : "DrawingView", element: ElementMixin) -> None:
        scene : DrawingScene = self.scene()
        dialog = PropertiesDialog(element)
        if dialog.exec():
            scene.editProperties(element, dialog.getChanges())
        self.state.go(self.stateIdle)

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
