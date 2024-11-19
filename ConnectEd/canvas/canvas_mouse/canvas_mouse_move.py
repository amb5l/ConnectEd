class CanvasMouseMoveMixin:
    '''
    Handle mouse movement when no button is pressed.
    Modifiers:
    CTRL    has no effect
    SHIFT   allows any angle drawing for wires and lines
    ALT     has no effect
    '''
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
            case self.State.PLACE_POLYLINE_1:
                pass
                # shift allows any angle