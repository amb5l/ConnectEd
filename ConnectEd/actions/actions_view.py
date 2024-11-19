from ._actions_private import _actions_todo


class ActionsViewMixin:
    def viewGrid(self):
        _actions_todo()

    def viewTransparent(self):
        _actions_todo()

    def viewOpaque(self):
        _actions_todo()

    def viewZoomIn(self):
        self.parent.canvas.zoomIn()

    def viewZoomOut(self):
        self.parent.canvas.zoomOut()

    def viewZoomWindow(self):
        self.parent.canvas.setState(self.parent.canvas.State.ZOOM)

    def viewZoomFull(self):
        self.parent.canvas.zoomFull()

    def viewPanLeft(self):
        self.parent.canvas.panLeft()

    def viewPanRight(self):
        self.parent.canvas.panRight()

    def viewPanUp(self):
        self.parent.canvas.panUp()

    def viewPanDown(self):
        self.parent.canvas.panDown()