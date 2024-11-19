from PyQt6.QtCore import QPointF, QRectF

from prefs import prefs

class DiagramSheet:
    def __init__(self, size):
        self.size = size

    def paint(self, painter):
        painter.fillRect(QRectF(
                QPointF(0, 0),
                self.size
            ),
            prefs.draw.theme.sheet
        )
