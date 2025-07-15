from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QCursor

from .....core import logger

from ....dialogs import TextDialog, PlaceBlockPinDialog

from ...scenes import DrawingScene
from ...items  import TextBlock, Block

from ...items.pin import BlockPin

from .defs import DrawingViewState as State

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


class DrawingViewPlaceMixin:
    def placeBlock(self : "DrawingView") -> None:
        self._goState(State.PlaceBlock1)

    def placeBlockBegin(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeBlock(pos)
        element.setSelected(True)
        self.wip.element = element
        self.wip.pos0 = pos
        self._goState(State.PlaceBlock2)

    def placeBlockContinue(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos0, pos, inst=self.wip.element)

    def placeBlockComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos0, pos, inst=self.wip.element)
        self.wip.clear()
        self._goState(State.Idle)

    def placeBlockPin(self : "DrawingView") -> None:
        if not self.placeBlockPinBegin():
            self.scene().clearSelection()
            self._goState(State.PlaceBlockPin1)

    def placeBlockPinBegin(self : "DrawingView") -> bool:
        selected_items = [item for item in self.scene().selectedItems() \
                          if item.parentItem() is None]
        if len(selected_items) == 1 and isinstance(selected_items[0], Block):
            self.wip.element = selected_items[0]
            self.wip.pos0 = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.placeBlockPinDialog()
            return True
        return False

    def placeBlockPinDialog(self : "DrawingView") -> None:
        dialog = PlaceBlockPinDialog()
        if dialog.exec():
            block : Block = self.wip.element
            name = dialog.getName()
            direction = dialog.getDirection()
            range = dialog.getRange()
            pin = BlockPin(
                name, direction, range,
                block.getEdgeLoc(
                    self.wip.pos0,
                    self.grid.pitch if self.grid.snap else None
                ),
                block
            )
            self.wip.element = pin
            self._goState(State.PlaceBlockPin2)
        else:
            self.wip.clear()
            self._goState(State.Idle)

    def placeBlockPinContinue(self : "DrawingView", pos : QPointF) -> None:
        pin : BlockPin = self.wip.element
        pin.setLocPos(pos, self.grid.pitch if self.grid.snap else None)

    def placeBlockPinComplete(self : "DrawingView", pos : QPointF) -> None:
        pin : BlockPin = self.wip.element
        pin.setLocPos(pos, self.grid.pitch if self.grid.snap else None)
        self.wip.clear()
        self._goState(State.Idle)

    def placeRectangle(self : "DrawingView") -> None:
        self._goState(State.PlaceRectangle1)

    def placeRectangleBegin(self : "DrawingView", p1: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeRectangle(p1)
        element.setSelected(True)
        self.wip.element = element
        self.wip.pos0 = p1
        self._goState(State.PlaceRectangle2)

    def placeRectangleContinue(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.element)

    def placeRectangleComplete(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.element)
        self.wip.clear()
        self._goState(State.Idle)

    def placeTextBlock(self : "DrawingView") -> None:
        self._goState(State.PlaceTextBlock1)

    def placeTextBlockBegin(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeTextBlock("", pos)
        element.setEditable(True)
        element.setFocus()
        self.wip.element = element
        self.wip.pos0 = pos
        self._goState(State.PlaceTextBlock2)

    def placeTextBlockComplete(self : "DrawingView") -> None:
        self.wip.element.clearFocus()

    def placeTextBlockFinalize(self : "DrawingView", text_item: TextBlock):
        scene : DrawingScene = self.scene()
        if text_item == self.wip.element:
            text = text_item.toPlainText()
            if text:
                self.wip.element.setEditable(False)
                self.wip.element.update()
                scene.placeTextBlock(text, self.wip.pos0, inst=self.wip.element)
            else: # cancel empty text
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextBlockFinalize: text_item != wip.element")
        self.wip.clear()
        self._goState(State.Idle)

    def placeText(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        element = scene.placeText("<text>", pos)
        element.setSelected(True)
        self.wip.clear()
        self.wip.element = element
        dialog = TextDialog(element)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setText(text)
            element.appearance.text.setPref(appearance)
            element.setPos(
                self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            )
            self._goState(State.PlaceText)
        else:
            self.wip.clear()

    def placeTextContinue(self : "DrawingView", pos : QPointF) -> None:
        self.wip.element.setPos(pos)

    def placeTextComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeText(pos, inst=self.wip.element)
        self.wip.clear()
        self._goState(State.Idle)
