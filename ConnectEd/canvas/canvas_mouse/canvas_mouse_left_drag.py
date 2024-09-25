class CanvasMouseLeftDrag:
    def mouseLeftDragStart(self, p):
        if (self.state == self.State.SELECT) \
        and (self.mouseModifiers & self.Modifiers.CTRL):
            pass
        else:
            self.selectionClear()
        match self.state:
            case self.State.SELECT:
                # click on background -> select area (new)
                # ctrl-click on background -> select area (incremental)
                # click on object(s) -> select and move it
                # ctrl-click on object(s) -> duplication
                items = self.diagram.select(p)
                if items:
                    self.selectionAdd(items)
                    if self.mouseModifiers & self.Modifiers.CTRL:
                        self.setState(self.State.DUPLICATE)
                    elif self.mouseModifiers & self.Modifiers.ALT:
                        self.setState(self.State.MOVE)
                    else:
                        self.setState(self.State.SLIDE)
                else:
                    self.setState(self.State.SELECT_AREA)
            case self.State.PLACE_BLOCK_0:
                self.setState(self.State.PLACE_BLOCK_1)


                if self.mouseModifiers & self.Modifiers.CTRL:
                    self.setState(self.State.DUPLICATE)

    def mouseLeftDrag(self, p):
        match self.state:
            case self.State.SELECT_AREA:
                self.selectionRect = self.saneRect(self.mousePressPos, p)

    def mouseLeftDragFinish(self, p2, p1):
        match self.state:
            case self.State.SELECT_AREA:
                self.selectionAdd(self.diagram.select(QRectF(p1, p2)))
                self.setState(self.State.SELECT)
            case self.State.DUPLICATE:
                # duplicate selected items at pos
                # back to select mode
                self.setState(self.State.SELECT)
            case self.State.MOVE:
                # move selected items to pos
                # back to select mode
                self.setState(self.State.SELECT)