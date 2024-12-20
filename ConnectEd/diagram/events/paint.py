from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush

from settings import settings


class DiagramEventsPaintMixin:
    def paint(self, painter):
        # sheet
        theme = settings.theme
        pen = QPen(theme.sheet, 0, Qt.PenStyle.NoPen)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.sheet)
        painter.fillRect(QRectF(0, 0, self.data.sheet.width(), self.data.sheet.height()), theme.sheet)
        # border
        #pen = QPen(theme.border.line, 0)
        #brush = QBrush(Qt.BrushStyle.NoBrush)
        #painter.setPen(pen)
        ## content
        ## WIP
