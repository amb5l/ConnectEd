class CanvasMouseMoveMixin:
    # movement with no button pressed
    def mouseMove(self, p):
        match self.state:
            case self.State.SELECT:
                pass
            case self.State.SELECT_WIN:
                self.selectionRect.setRect(self.saneRect(self.mousePressPos, p))
            case self.State.PLACE_BLOCK_0:
                pass
            case self.State.PLACE_BLOCK_1:
                self.diagram.newBlockResize(self.snap(p))