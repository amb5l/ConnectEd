from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF, pyqtSignal
from PyQt6.QtGui  import QPainter, QPen, QBrush

from .....app import settings

from .....core.check   import checked
from .....core.types   import DataKind

from ...properties import InherentProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....documents.schematic import HdlSchematicDiagramDoc

from ..drawing import DrawingScene

from .api       import DiagramSceneApiMixin
from .xml       import DiagramSceneXmlMixin
from .resources import DiagramSceneResources

from .netlist import Netlist

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.symbol import SymbolDefinitionItem, SymbolInstanceItem


@dataclass
class DiagramSheet:
    name : str
    rect : QRectF


class DiagramScene(DiagramSceneApiMixin, DiagramSceneXmlMixin, DrawingScene):
    # class attributes
    _RESOURCES_CLS = DiagramSceneResources
    _PROPERTIES = DrawingScene._PROPERTIES | {
        "Sheet Name" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.getSheetName(),
            setter = lambda self, value: self.setSheetName(value)
        ),
        "Sheet Width" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetWidth(),
            setter = lambda self, value: self.setSheetWidth(value)
        ),
        "Sheet Height" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetHeight(),
            setter = lambda self, value: self.setSheetHeight(value)
        ),
        "Margin" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.margin,
            setter = lambda self, value: self.setMargin(value)
        ),
        "Border" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.border,
            setter = lambda self, value: self.setBorder(value)
        )
    }

    # instance attributes
    _doc        : "HdlSchematicDiagramDoc | None"
    _symbols    : dict[str, "SymbolDefinitionItem"]
    sheet       : DiagramSheet
    margin      : float                  # distance from paper edge to border line
    border      : float                  # line width
    title_block : SymbolInstanceItem | None
    resources   : DiagramSceneResources
    netlist     : Netlist

    # signals
    netlistChanged = pyqtSignal()  # noqa N815

    @checked
    def __init__(
        self  : Self,
        doc   : "HdlSchematicDiagramDoc | None" = None,
        fresh : bool = True
    ) -> None:
        sheet_name   = settings().get("defaults/sheet/name")
        sheet_size   = settings().get("defaults/sheet/size")
        sheet_rect   = QRectF(QPointF(0, 0), sheet_size)
        self.sheet   = DiagramSheet(sheet_name, sheet_rect)
        self.margin  = settings().get("defaults/margin")
        self.border  = settings().get("defaults/border")
        super().__init__(doc, sheet_size, fresh)
        self._symbols = {}
        self.netlist = Netlist(self)

    @checked
    def updateSceneRect(
        self         : Self,
        rect_or_size : QRectF | QSizeF | None = None,
    ) -> None:
        super().updateSceneRect(self.sheet.rect)  # sheet is minimum rect

    @checked
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

    def symbolDefinitions(self : Self) -> dict[str, "SymbolDefinitionItem"]:
        return self._symbols

    @checked
    def getSheetName(self : Self) -> str:
        return self.sheet.name

    @checked
    def setSheetName(self : Self, name : str) -> None:
        self.sheet.name = name
        self.properties.signalChanges("Sheet Name")

    @checked
    def getSheetWidth(self : Self) -> float:
        return self.sheet.rect.width()

    @checked
    def setSheetWidth(self : Self, width : float) -> None:
        self.sheet.rect.setWidth(width)
        self.updateSceneRect()
        self.update()
        self.properties.signalChanges("Sheet Width")

    @checked
    def getSheetHeight(self : Self) -> float:
        return self.sheet.rect.height()

    @checked
    def setSheetHeight(self : Self, height : float) -> None:
        self.sheet.rect.setHeight(height)
        self.updateSceneRect()
        self.update()
        self.properties.signalChanges("Sheet Height")

    @checked
    def getMargin(self : Self) -> float:
        return self.margin

    @checked
    def setMargin(self : Self, margin : float) -> None:
        self.margin = margin
        self.update()
        self.properties.signalChanges("Margin")

    @checked
    def getBorder(self : Self) -> float:
        return self.border

    @checked
    def setBorder(self : Self, border : float) -> None:
        self.border = border
        self.update()
        self.properties.signalChanges("Border")
