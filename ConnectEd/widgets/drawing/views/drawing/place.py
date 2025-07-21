from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QCursor

from .....core import logger

from ....dialogs import TextDialog, PlacePortPinDialog

from ...scenes import DrawingScene
from ...items  import TextBlock, Block

from ...items.pin  import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


class DrawingViewPlaceMixin:
    def placePort(self : "DrawingView") -> None:
        dialog = PlacePortPinDialog("Port")
        self.state.go(self.statePlacePort1)
        if dialog.exec():
            name = dialog.getName()
            direction = dialog.getDirection()
            range = dialog.getRange()
            pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            scene : DrawingScene = self.scene()
            port = scene.placePort(name, direction, range, pos)
            self.wip.element = port
            self.state.go(self.statePlacePort2)
        else:
            self.wip.clear()
            self.state.go(self.stateIdle)

    def placePortContinue(self : "DrawingView", pos : QPointF) -> None:
        self.wip.element.setPos(pos)

    def placePortComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placePort(pos, inst=self.wip.element)
        self.wip.clear()
        self.state.go(self.stateIdle)

    def placeBlock(self : "DrawingView") -> None:
        self.state.go(self.statePlaceBlock1)

    def placeBlockBegin(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeBlock(pos)
        element.setSelected(True)
        self.wip.element = element
        self.wip.pos = pos
        self.state.go(self.statePlaceBlock2)

    def placeBlockContinue(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos, pos, inst=self.wip.element)

    def placeBlockComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos, pos, inst=self.wip.element)
        self.wip.clear()
        self.state.go(self.stateIdle)

    def placeBlockPin(self : "DrawingView") -> None:
        if not self.placeBlockPinBegin():
            self.scene().clearSelection()
            self.state.go(self.statePlaceBlockPin1)

    def placeBlockPinBegin(self : "DrawingView") -> bool:
        selected_items = [item for item in self.scene().selectedItems() \
                          if item.parentItem() is None]
        if len(selected_items) == 1 and isinstance(selected_items[0], Block):
            self.wip.element = selected_items[0]
            self.wip.pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.placeBlockPinDialog()
            return True
        return False

    def placeBlockPinDialog(self : "DrawingView") -> None:
        dialog = PlacePortPinDialog("Block Pin")
        self.state.go(self.statePlaceBlockPin2)
        if dialog.exec():
            block : Block = self.wip.element
            name = dialog.getName()
            direction = dialog.getDirection()
            range = dialog.getRange()
            pin = BlockPin(
                name, direction, range,
                block.getEdgeLoc(
                    self.wip.pos,
                    self.grid.pitch if self.grid.snap else None
                ),
                block
            )
            self.wip.element = pin
            self.state.go(self.statePlaceBlockPin3)
        else:
            self.wip.clear()
            self.state.go(self.stateIdle)

    def placeBlockPinContinue(self : "DrawingView", pos : QPointF) -> None:
        pin : BlockPin = self.wip.element
        pin.setLocPos(pos, self.grid.pitch if self.grid.snap else None)

    def placeBlockPinComplete(self : "DrawingView", pos : QPointF) -> None:
        pin : BlockPin = self.wip.element
        pin.setLocPos(pos, self.grid.pitch if self.grid.snap else None)
        self.wip.clear()
        self.state.go(self.stateIdle)

    def placeRectangle(self : "DrawingView") -> None:
        self.state.go(self.statePlaceRectangle1)

    def placeRectangleBegin(self : "DrawingView", p1: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeRectangle(p1)
        element.setSelected(True)
        self.wip.element = element
        self.wip.pos = p1
        self.state.go(self.statePlaceRectangle2)

    def placeRectangleContinue(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos, p2, inst=self.wip.element)

    def placeRectangleComplete(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos, p2, inst=self.wip.element)
        self.wip.clear()
        self.state.go(self.stateIdle)

    def placeTextBlock(self : "DrawingView") -> None:
        self.state.go(self.statePlaceTextBlock1)

    def placeTextBlockBegin(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeTextBlock("", pos)
        element.setEditable(True)
        element.setFocus()
        self.wip.element = element
        self.wip.pos = pos
        self.state.go(self.statePlaceTextBlock2)

    def placeTextBlockComplete(self : "DrawingView") -> None:
        self.wip.element.clearFocus()

    def placeTextBlockFinalize(self : "DrawingView", text_item: TextBlock):
        scene : DrawingScene = self.scene()
        if text_item == self.wip.element:
            text = text_item.toPlainText()
            if text:
                self.wip.element.setEditable(False)
                self.wip.element.update()
                scene.placeTextBlock(text, self.wip.pos, inst=self.wip.element)
            else: # cancel empty text
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextBlockFinalize: text_item != wip.element")
        self.wip.clear()
        self.state.go(self.stateIdle)

    def placeText(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        element = scene.placeText("<text>", pos)
        element.setSelected(True)
        self.wip.clear()
        self.wip.element = element
        dialog = TextDialog(element)
        self.state.go(self.statePlaceText1)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setText(text)
            element.appearance.text.setPref(appearance)
            element.setPos(
                self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            )
            self.state.go(self.statePlaceText2)
        else:
            self.wip.clear()

    def placeTextContinue(self : "DrawingView", pos : QPointF) -> None:
        self.wip.element.setPos(pos)

    def placeTextComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeText(pos, inst=self.wip.element)
        self.wip.clear()
        self.state.go(self.stateIdle)
