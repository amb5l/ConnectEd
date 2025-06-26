from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QCursor

from .....core import logger

from ....dialogs import TextDialog

from ...scenes import DrawingScene
from ...items  import TextBlock, TextLine

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
        self.wip.elements = [element]
        self.wip.pos0 = pos
        self._goState(State.PlaceBlock2)

    def placeBlockContinue(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos0, pos, inst=self.wip.elements[0])

    def placeBlockComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeBlock(self.wip.pos0, pos, inst=self.wip.elements[0])
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
        self.wip.elements = [element]
        self.wip.pos0 = p1
        self._goState(State.PlaceRectangle2)

    def placeRectangleContinue(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])

    def placeRectangleComplete(self : "DrawingView", p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])
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
        self.wip.elements = [element]
        self.wip.pos0 = pos
        self._goState(State.PlaceTextBlock2)

    def placeTextBlockComplete(self : "DrawingView") -> None:
        self.wip.elements[0].clearFocus()

    def placeTextBlockFinalize(self : "DrawingView", text_item: TextBlock):
        scene : DrawingScene = self.scene()
        if text_item == self.wip.elements[0]:
            text = text_item.toPlainText()
            if text:
                self.wip.elements[0].setEditable(False)
                self.wip.elements[0].update()
                scene.placeTextBlock(text, self.wip.pos0, inst=self.wip.elements[0])
            else: # cancel empty text
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextBlockFinalize: text_item != wip.elements[0]")
        self.wip.clear()
        self._goState(State.Idle)

    def placeTextLine(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        element = scene.placeTextLine("<text>", pos)
        element.setSelected(True)
        self.wip.clear()
        self.wip.elements = [element]
        dialog = TextDialog(element)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setText(text)
            element.appearance.text.setPref(appearance)
            element.setPos(
                self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            )
            self._goState(State.PlaceTextLine)
        else:
            self.wip.clear()

    def placeTextLineContinue(self : "DrawingView", pos : QPointF) -> None:
        self.wip.elements[0].setPos(pos)

    def placeTextLineComplete(self : "DrawingView", pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeTextLine(pos, inst=self.wip.elements[0])
        self.wip.clear()
        self._goState(State.Idle)
