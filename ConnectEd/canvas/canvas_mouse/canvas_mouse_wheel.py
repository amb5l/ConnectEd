class CanvasMouseWheelMixin:
    def wheelCtrlShiftAlt(self, event):
        pass

    def wheelCtrlShift(self, event):
        pass

    def WheelCtrlAlt(self, event):
        pass

    def wheelShiftAlt(self, event):
        pass

    def wheelCtrl(self, event):
        pass

    def WheelShift(self, event):
        pass

    def wheelAlt(self, event):
        pass

    def wheel(self, event):
        delta = event.angleDelta().y()/prefs().view.wheelStep
        if delta > 0:
            self.zoomIn(delta)
        elif delta < 0:
            self.zoomOut(-delta)

