__all__ = ["DiagramScene"]

from typing import Self, Optional

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui  import QPainter, QPen, QBrush

from . import DrawingScene

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core import Diagram


class DiagramScene(DrawingScene):
    XML_ATTRS = DrawingScene.XML_ATTRS | {
        "paper_size" : "str",
        "margin"     : "float",
        "border"     : "float"
    }

    paper_size : str | QSizeF
    margin     : float # distance from paper edge to border line
    border     : float # line width

    def __init__(
        self,
        parent     : "Diagram",
        paper_size : Optional[str | QSizeF] = None,
        margin     : Optional[float] = None,
        border     : Optional[float] = None
    ) -> None:
        super().__init__(parent)
        if paper_size is None:
            paper_size = hub.settings.get("defaults/paper_size")
        if margin is None:
            margin = hub.settings.get("defaults/margin")
        if border is None:
            border = hub.settings.get("defaults/border")
        self.paper_size = paper_size
        self.margin = margin
        self.border = border
        paper_rect = self.paper_rect()
        self.setSceneRect(QRectF(
            QPointF(-paper_rect.width(), -paper_rect.height()),
            QSizeF(paper_rect.width() * 3, paper_rect.height() * 3)
        ))

    def paper_rect(self : Self) -> QRectF:
        size = self.paper_size
        if isinstance(size, str):
            size = hub.settings.get(f"paper_sizes/{size}")
        return QRectF(QPointF(0, 0), size)

    def drawBackground(self : Self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, hub.settings.getTheme("background/fill"))
        painter.fillRect(
            self.paper_rect(),
            hub.settings.getTheme("paper/fill")
        )
        painter.setPen(QPen(
            hub.settings.getTheme("border/line"),
            self.border,
            Qt.PenStyle.SolidLine
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.paper_rect().adjusted(
            self.margin, self.margin, -self.margin, -self.margin
        ))
