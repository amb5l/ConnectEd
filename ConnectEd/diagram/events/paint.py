from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush

from settings import settings


class DiagramEventsPaintMixin:
    def paint(self, painter):
        pass
        ## sheet
        #painter.fillRect(self.data.size, theme.background)
        ## border
        #pen = QPen(theme.border.line, 0)
        #brush = QBrush(Qt.BrushStyle.NoBrush)
        #painter.setPen(pen)
        ## content
        ## WIP
