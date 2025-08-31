from typing import Self, Optional
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui  import QPainter, QPen, QBrush

from .drawing import DrawingScene

from ..properties import PropertySpec

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import DiagramItem

@dataclass
class DiagramSheet:
    name : str
    rect : QRectF

class DiagramScene(DrawingScene):
    # class attributes
    _PROPERTY_SPECS = DrawingScene._PROPERTY_SPECS | {
        "Sheet Name" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self.getSheetName(),
            setter    = lambda self, value: self.setSheetName(value)
        ),
        "Sheet Width" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.getSheetWidth(),
            setter    = lambda self, value: self.setSheetWidth(value)
        ),
        "Sheet Height" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.getSheetHeight(),
            setter    = lambda self, value: self.setSheetHeight(value)
        ),
        "Margin" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.margin,
            setter    = lambda self, value: self.setMargin(value)
        ),
        "Border" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.border,
            setter    = lambda self, value: self.setBorder(value)
        )
    }

    # instance attributes
    sheet  : DiagramSheet
    margin : float         # distance from paper edge to border line
    border : float         # line width

    def __init__(self : Self, parent : Optional["DiagramItem"] = None) -> None:
        super().__init__(parent)
        sheet_name = hub.settings.get("defaults/sheet/name")
        sheet_size = hub.settings.get("defaults/sheet/size")
        sheet_rect = QRectF(QPointF(0, 0), sheet_size)
        self.sheet = DiagramSheet(sheet_name, sheet_rect)
        self.margin = hub.settings.get("defaults/margin")
        self.border = hub.settings.get("defaults/border")
        self.updateSceneRect()

    def drawBackground(self : Self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, hub.settings.getTheme("background"))
        painter.fillRect(
            self.sheet.rect,
            hub.settings.getTheme("sheet")
        )
        painter.setPen(QPen(
            hub.settings.getTheme("border"),
            self.border,
            Qt.PenStyle.SolidLine
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.sheet.rect.adjusted(
            self.margin, self.margin, -self.margin, -self.margin
        ))

    def updateSceneRect(self : Self) -> None:
        self.setSceneRect(QRectF(
            QPointF(-self.sheet.rect.width(), -self.sheet.rect.height()),
            QSizeF(self.sheet.rect.width() * 3, self.sheet.rect.height() * 3)
        ))

    def getSheetName(self : Self) -> str:
        return self.sheet.name

    def setSheetName(self : Self, name : str) -> None:
        self.sheet.name = name

    def getSheetWidth(self : Self) -> float:
        return self.sheet.rect.width()

    def setSheetWidth(self : Self, width : float) -> None:
        self.sheet.rect.setWidth(width)
        self.updateSceneRect()
        self.update()

    def getSheetHeight(self : Self) -> float:
        return self.sheet.rect.height()

    def setSheetHeight(self : Self, height : float) -> None:
        self.sheet.rect.setHeight(height)
        self.updateSceneRect()
        self.update()

    def getMargin(self : Self) -> float:
        return self.margin

    def setMargin(self : Self, margin : float) -> None:
        self.margin = margin
        self.update()

    def getBorder(self : Self) -> float:
        return self.border

    def setBorder(self : Self, border : float) -> None:
        self.border = border
        self.update()
