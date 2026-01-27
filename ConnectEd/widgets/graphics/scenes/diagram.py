from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui  import QPainter, QPen, QBrush

from ....app import settings

from ..property   import PropertySpec

from .drawing import DrawingScene


@dataclass
class DiagramSheet:
    name : str
    rect : QRectF


class DiagramScene(DrawingScene):
    # class attributes
    _PROPERTIES = DrawingScene._PROPERTIES | {
        "Sheet Name" : PropertySpec(
            getter = lambda self: self.getSheetName(),
            setter = lambda self, value: self.setSheetName(value)
        ),
        "Sheet Width" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.getSheetWidth(),
            setter = lambda self, value: self.setSheetWidth(value)
        ),
        "Sheet Height" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.getSheetHeight(),
            setter = lambda self, value: self.setSheetHeight(value)
        ),
        "Margin" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.margin,
            setter = lambda self, value: self.setMargin(value)
        ),
        "Border" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.border,
            setter = lambda self, value: self.setBorder(value)
        )
    }

    # instance attributes
    sheet  : DiagramSheet
    margin : float         # distance from paper edge to border line
    border : float         # line width

    def __init__(self : Self) -> None:
        sheet_name = settings().get("defaults/sheet/name")
        sheet_size = settings().get("defaults/sheet/size")
        sheet_rect = QRectF(QPointF(0, 0), sheet_size)
        self.sheet = DiagramSheet(sheet_name, sheet_rect)
        self.margin = settings().get("defaults/margin")
        self.border = settings().get("defaults/border")
        super().__init__(sheet_size)

    def updateSceneRect(self : Self, rect : QRectF | None = None) -> None:
        super().updateSceneRect(self.sheet.rect)  # sheet is minimum rect

    def drawBackground(self : Self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, settings().get("theme/background"))
        painter.fillRect(
            self.sheet.rect,
            settings().get("theme/sheet")
        )
        painter.setPen(QPen(
            settings().get("theme/border"),
            self.border,
            Qt.PenStyle.SolidLine
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.sheet.rect.adjusted(
            self.margin, self.margin, -self.margin, -self.margin
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
