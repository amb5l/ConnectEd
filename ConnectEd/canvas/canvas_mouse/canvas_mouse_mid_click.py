class CanvasMouseClickMixin:
    def mouseClick(self, p):
        if self.mouseButton == self.MouseButton.LEFT:
            pass
        match self.state:
            case self.State.SELECT:
                if not self.mouseModifiers & self.Modifiers.CTRL:
                    self.selectionClear()
                self.selectionAdd(self.diagram.select(p))
                self.update()
            case self.State.SELECT_WIN_0:
                if not self.mouseModifiers & self.Modifiers.CTRL:
                    self.selectionClear()
                self.selectionRect.setRect(self.saneRect(p, p))
                self.setState(self.State.SELECT_WIN_1)
            case self.State.SELECT_WIN_1:
                self.selectionRect.setRect(self.saneRect(self.prevPos, p))
                self.selectionAdd(self.diagram.select(self.selectionRect))
                self.setState(self.State.SELECT)
            case self.State.PASTE:
                # pasteBuffer contains copy origin
                self.diagram.paste(self.pasteBuffer, p)
            case self.State.PLACE_BLOCK_0:
                self.diagram.newBlockStart(self.snap(p))
                self.setState(self.State.PLACE_BLOCK_1)
                self.update()
            case self.State.PLACE_BLOCK_1:
                self.diagram.newBlockFinish(self.snap(p))
                self.setState(self.State.PLACE_BLOCK_1)
                self.update()
            case _:
                logger.warning(
                    "Canvas.mouseClick: unexpected mode:",
                    str(self.state)
                )
        self.prevPos = p