from PyQt6.QtCore import QPointF, QRectF

from prefs import prefs


class CanvasPrivateMixin:
    # snaps from minor to major grid
    def snap(self, position):
        return QPointF(
            int(round(position.x()/10.0, 0) * 10),
            int(round(position.y()/10.0, 0) * 10)
        )

    def canvas2diagram(self, point):
        # convert canvas point to diagram point
        r = QPointF(
            (point.x() / self.zoom) + self.pan.x(),
            (point.y() / self.zoom) + self.pan.y()
        )
        return r

    def _actionEnable(self, menuName, actionName, state):
        self.parent().menuBar.menusDict[menuName].itemsDict[actionName].setEnabled(state)

    def _unexpectedEditState(self):
        self.logger.warning("Canvas.mouseReleaseEvent: unexpected editState: " + str(self.State))
