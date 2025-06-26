from PyQt6.QtCore import QPointF

from .....core import logger, paste

from ....dialogs import AppearanceDialog, PropertiesDialog, PropertyValuesDialog

from ...scenes import DrawingScene
from ...items  import ElementMixin, KeyPoint

from .defs import DrawingViewState as State

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
        self._goState(State.Idle)

    def editComplete(self : "DrawingView") -> None:
        # TODO seriously consider this
        match self.state:
            case State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.current.logical)
                )

    def editCut(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editCut(self._snap(self.mouse.current.logical))

    def editCopy(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        self.wip.clear()
        items, copy_pos = paste()
        if not items:
            logger.warning("No valid data to paste")
            self._goState(State.Idle)
            return
        elements = [item for item in items if isinstance(item, ElementMixin)]
        if not elements:
            logger.warning("No valid elements to paste")
            self._goState(State.Idle)
            return
        # Capture the current selection before clearing
        selection = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]
        # Clear selection and hide keypoints
        scene.clearSelection()
        for item in scene.items():
            if isinstance(item, ElementMixin):
                item.setKPVisible(False)
        self.wip.elements = elements
        # Calculate offset from copy position to current mouse position
        current_pos = self._snap(self.mouse.current.logical)
        copy_pos = copy_pos if copy_pos is not None else \
            (elements[0].pos() if elements else QPointF(0, 0))
        offset = current_pos - copy_pos
        # Set current position as reference for future mouse movement
        self.wip.pos0 = current_pos
        scene.blockSignals(True)
        for element in elements:
            if element.scene() != scene:
                scene.addItem(element)
            # Apply initial offset to position elements at mouse location
            element.setPos(element.pos() + offset)
            element.setSelected(True)
            element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        scene.selectionChanged.emit()
        self.wip.macro = True
        self.wip.selection = selection  # Store for use in editPasteComplete
        scene.undo_stack.beginMacro("Paste Elements")
        self._goState(State.EditPaste)

    def editPasteContinue(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editPasteContinue: No elements in wip, aborting")
            self._goState(State.Idle)
            return
        new_pos = self._snap(self.mouse.current.logical)
        mouse_delta = new_pos - self.wip.pos0
        # Block signals to avoid multiple selection updates
        scene.blockSignals(True)
        for element in self.wip.elements:
            if element.scene() == scene:
                element.setPos(element.pos() + mouse_delta)
                element.setSelected(True)  # Ensure elements remain selected
                element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        # Manually trigger selection changed to update key points
        scene.selectionChanged.emit()
        self.wip.pos0 = new_pos

    def editPasteComplete(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editPasteComplete: No elements in wip, aborting")
            self._goState(State.Idle)
            return
        pos = self._snap(self.mouse.current.logical)
        offset = pos - self.wip.pos0
        for element in self.wip.elements:
            if element.scene() == scene:
                scene.removeItem(element)
                element.setPos(element.pos() - offset)
        # Pass the original selection to editPaste
        scene.editPaste(pos, (self.wip.elements, self.wip.pos0, self.wip.selection))
        if self.wip.macro:
            scene.undo_stack.endMacro()
        self.wip.clear()
        self._goState(State.Idle)

    def editDelete(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.editDelete()

    def editDuplicate(self : "DrawingView", pos: QPointF = None) -> None:
        scene : DrawingScene = self.scene()
        elements = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]
        if not elements:
            # Enter selection mode if nothing is selected
            self._goState(State.EditDuplicate1)
            return
        # Start duplication with selected elements
        self.wip.clear()
        # Store original selection before clearing
        selection = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]
        # Clone the elements
        cloned_elements = []
        for element in elements:
            try:
                clone = element.clone()
                cloned_elements.append(clone)
            except Exception as e:
                logger.warning(f"Failed to clone element {element}: {e}")
        if not cloned_elements:
            logger.warning("editDuplicate: Failed to clone elements")
            return
        # Clear selection and hide keypoints
        scene.clearSelection()
        for item in scene.items():
            if isinstance(item, ElementMixin):
                item.setKPVisible(False)
        self.wip.elements = cloned_elements
        # Use provided position or current mouse position
        self.wip.pos0 = pos if pos is not None else self._snap(self.mouse.current.logical)
        # Don't apply any initial offset - keep cloned elements at their original positions
        scene.blockSignals(True)
        for element in cloned_elements:
            if element.scene() != scene:
                scene.addItem(element)
            element.setSelected(True)
            element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        scene.selectionChanged.emit()
        self.wip.macro = True
        self.wip.selection = selection  # Store for use in editDuplicateComplete
        scene.undo_stack.beginMacro("Duplicate Elements")
        self._goState(State.EditDuplicate2)

    def editDuplicateContinue(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editDuplicateContinue: No elements in wip, aborting")
            self._goState(State.Idle)
            return
        new_pos = self._snap(self.mouse.current.logical)
        mouse_delta = new_pos - self.wip.pos0
        # Block signals to avoid multiple selection updates
        scene.blockSignals(True)
        for element in self.wip.elements:
            if element.scene() == scene:
                element.setPos(element.pos() + mouse_delta)
                element.setSelected(True)  # Ensure elements remain selected
                element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        # Manually trigger selection changed to update key points
        scene.selectionChanged.emit()
        self.wip.pos0 = new_pos

    def editDuplicateComplete(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editDuplicateComplete: No elements in wip, aborting")
            self._goState(State.Idle)
            return
        pos = self._snap(self.mouse.current.logical)
        offset = pos - self.wip.pos0
        # Remove temporary elements from scene before final placement
        for element in self.wip.elements:
            if element.scene() == scene:
                scene.removeItem(element)
                element.setPos(element.pos() - offset)
        # Use the original selection to determine what was duplicated
        original_elements = self.wip.selection if self.wip.selection else []
        # Pass the cloned elements to editDuplicate for final placement
        scene.editDuplicate(pos, (self.wip.elements, self.wip.pos0, original_elements))
        if self.wip.macro:
            scene.undo_stack.endMacro()
        self.wip.clear()
        self._goState(State.Idle)

    def editSlide(self : "DrawingView") -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.editMoveBegin(self.scene().selectedItems(), pos, True)
        else:
            self._goState(State.EditSlide1)

    def editMove(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        if scene.selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.editMoveBegin(scene.selectedItems(), pos)
            self._goState(State.EditMove2)
        else:
            self._goState(State.EditMove1)

    def editMoveBegin(
        self     : "DrawingView",
        elements : list[ElementMixin],
        pos      : QPointF,
        slide    : bool = False
    ) -> None:
        self.wip.elements = elements
        if isinstance(elements[0], KeyPoint):
            pos = elements[0].scenePos()
        self.wip.pos0 = pos

    def editMoveContinue(
        self  : "DrawingView",
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        scene : DrawingScene = self.scene()
        scene.editMove(self.wip.elements, pos - self.wip.pos0, slide)
        self.wip.pos0 = pos

    def editMoveComplete(
        self  : "DrawingView",
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        scene : DrawingScene = self.scene()
        scene.editMove(self.wip.elements, pos - self.wip.pos0, slide)
        self.wip.clear()

    def editResize(self : "DrawingView") -> None:
        if len(self.scene().selectedItems()) == 1:
            self._goState(State.EditResize2)
        else:
            self.scene().clearSelection()
            self._goState(State.EditResize1)

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
            self._goState(State.EditAppearance2)
            dialog = AppearanceDialog(elements)
            if dialog.exec():
                scene.editAppearance(
                    elements,
                    dialog.getChoice()
                )
            self._goState(State.Idle)
        else:
            self._goState(State.EditAppearance1)

    def editProperties(self : "DrawingView", element: ElementMixin) -> None:
        scene : DrawingScene = self.scene()
        dialog = PropertiesDialog(element)
        if dialog.exec():
            scene.editProperties(element, dialog.getChoices())
        self._goState(State.Idle)

    def editPropertyValues(self : "DrawingView", elements: list[ElementMixin] = []) -> None:
        scene : DrawingScene = self.scene()
        if not elements:
            elements = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]
        if elements:
            dialog = PropertyValuesDialog(elements)
            if dialog.exec():
                scene.editPropertyValues(elements, dialog.getChoices())
            self._goState(State.Idle)
        else:
            logger.warning("No elements selected for properties editing")
