from typing import Self

from PyQt6.QtCore import QPointF

from .....core import logger

from ...scenes import DrawingScene
from ...items  import TextBlock

from .defs import DrawingViewState as State


class DrawingViewPlaceMixin:
    def placeRectangle(self : Self) -> None:
        self._goState(State.PlaceRectangle1)

    def placeRectangleBegin(self : Self, p1: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeRectangle(p1)
        self.wip.elements = [element]
        self.wip.pos0 = p1
        self.wip.elements[0].setSelected(True) # explicitly select the rectangle
        self.wip.elements[0].setKPVisible(True) # ensure keypoints are visible
        self._goState(State.PlaceRectangle2)

    def placeRectangleContinue(self : Self, p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])

    def placeRectangleComplete(self : Self, p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])
        self.wip.clear()
        self._goState(State.Idle)

    def placeTextBlock(self : Self) -> None:
        self._goState(State.PlaceTextBlock1)

    def placeTextBlockBegin(self : Self, pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeTextBlock("", pos)
        element.setEditable(True)
        element.setFocus()
        self.wip.elements = [element]
        self.wip.pos0 = pos
        self._goState(State.PlaceTextBlock2)

    def placeTextBlockComplete(self : Self) -> None:
        self.wip.elements[0].clearFocus()

    def placeTextBlockFinalize(self, text_item: TextBlock):
        scene : DrawingScene = self.scene()
        if text_item == self.wip.elements[0]:
            text = text_item.toPlainText()
            if text:
                self.wip.elements[0].setEditable(False)
                self.wip.elements[0].update()
                scene.placeTextBlock(text, self.wip.pos0, inst=self.wip.elements[0])
                scene.clearSelection()
                self.wip.elements[0].setSelected(True)
            else: # cancel empty text
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextBlockFinalize: text_item != wip.elements[0]")
        self.wip.clear()
        self._goState(State.Idle)