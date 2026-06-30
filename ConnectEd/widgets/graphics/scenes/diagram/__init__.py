from __future__ import annotations

import uuid

from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF, pyqtSignal
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack, QPainter, QPen, QBrush

from .....app import settings

from .....core.check   import checked
from .....core.types   import DataKind

from ...properties import PropertiesMixin, InherentProperty

from .api       import DiagramSceneApiMixin
from .grips     import DiagramSceneGripsMixin
from .guides    import DiagramSceneGuidesMixin
from .xml       import DiagramSceneXmlMixin
from .private   import DiagramScenePrivateMixin
from .resources import DiagramSceneResources

from .netlist import Netlist

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....documents.schematic import HdlSchematicDiagramDoc
    from ...items.symbol import SymbolDefinitionItem, SymbolInstanceItem


class DiagramScene(
    DiagramSceneApiMixin,
    DiagramSceneGripsMixin,
    DiagramSceneGuidesMixin,
    DiagramSceneXmlMixin,
    DiagramScenePrivateMixin,
    PropertiesMixin,
    QGraphicsScene
):
    # class attributes
    _RESOURCES_CLS = DiagramSceneResources
    _PROPERTIES = {
        "Name" : InherentProperty["DiagramScene"](
            kind   = DataKind.STR,
            getter = lambda self: self.name(),
            setter = lambda self, value: self.setName(value)
        ),
        "Sheet Name" : InherentProperty["DiagramScene"](
            kind   = DataKind.STR,
            getter = lambda self: self.getSheetName(),
            setter = lambda self, value: self.setSheetName(value)
        ),
        "Sheet Width" : InherentProperty["DiagramScene"](
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetWidth(),
            setter = lambda self, value: self.setSheetWidth(value)
        ),
        "Sheet Height" : InherentProperty["DiagramScene"](
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetHeight(),
            setter = lambda self, value: self.setSheetHeight(value)
        ),
        "Margin" : InherentProperty["DiagramScene"](
            kind   = DataKind.FLOAT,
            getter = lambda self: self._sheet_margin,
            setter = lambda self, value: self.setMargin(value)
        ),
        "Border" : InherentProperty["DiagramScene"](
            kind   = DataKind.FLOAT,
            getter = lambda self: self._sheet_border,
            setter = lambda self, value: self.setBorder(value)
        )
    }

    # instance attributes
    _uuid         : str
    _doc          : HdlSchematicDiagramDoc | None
    _name         : str
    _sheet_name   : str
    _sheet_rect   : QRectF
    _sheet_margin : float   # distance from paper edge to border line
    _sheet_border : float   # line width

    _symbols      : dict[str, SymbolDefinitionItem]

    resources     : DiagramSceneResources
    undo_stack    : QUndoStack
    title_block   : SymbolInstanceItem | None
    netlist       : Netlist

    # signals
    netlistChanged = pyqtSignal()  # noqa N815

    @checked
    def __init__(
        self  : Self,
        doc   : HdlSchematicDiagramDoc | None = None,
        fresh : bool = True
    ) -> None:

        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = "Untitled"
        self._sheet_name = settings().get("defaults/sheet/name")
        self._sheet_rect = QRectF(
            QPointF(0, 0), settings().get("defaults/sheet/size")
        )
        self._sheet_margin = settings().get("defaults/margin")
        self._sheet_border = settings().get("defaults/border")
        self.updateSceneRect()

        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.resources = self._RESOURCES_CLS()
        self.undo_stack = QUndoStack(self)
        self._doc = doc
        self.initProperties(fresh)
        self.initGrips()
        self.selectionChanged.connect(self.onSelectionChanged)
        self.setLive(fresh)

        self._symbols = {}
        self.netlist = Netlist(self)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DiagramScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSelectionChanged(self : Self) -> None:
        self.updateGrips()

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str, notify : bool = True) -> None:
        self._name = name
        self.properties.signalChanges("Name")
        if notify and self._doc is not None and self.live():
            self._doc.onChanged()

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(self : Self) -> None:
        # start with sheet rect x3
        w = self._sheet_rect.width()
        h = self._sheet_rect.height()
        scene_rect = QRectF(
            self._sheet_rect.left() - w,
            self._sheet_rect.top() - h,
            w * 3,
            h * 3
        )
        # unite with item rects
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            scene_rect = scene_rect.united(item_rect)
        # done
        self.setSceneRect(scene_rect)

    @checked
    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF | None
    ) -> None:
        if painter is None or rect is None:
            return
        # background
        painter.fillRect(rect, settings().get("theme/background"))
        # sheet
        painter.fillRect(
            self._sheet_rect,
            settings().get("theme/sheet")
        )
        painter.setPen(QPen(
            settings().get("theme/border"),
            self._sheet_border,
            Qt.PenStyle.SolidLine
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self._sheet_rect.adjusted(
            self._sheet_margin, self._sheet_margin,
            -self._sheet_margin, -self._sheet_margin
        ))

    def symbolDefinitions(self : Self) -> dict[str, SymbolDefinitionItem]:
        return self._symbols

    @checked
    def getSheetName(self : Self) -> str:
        return self._sheet_name

    @checked
    def setSheetName(self : Self, name : str) -> None:
        self._sheet_name = name
        self.properties.signalChanges("Sheet Name")

    @checked
    def getSheetWidth(self : Self) -> float:
        return self._sheet_rect.width()

    @checked
    def setSheetWidth(self : Self, width : float) -> None:
        self._sheet_rect.setWidth(width)
        self.updateSceneRect()
        self.update()
        self.properties.signalChanges("Sheet Width")

    @checked
    def getSheetHeight(self : Self) -> float:
        return self._sheet_rect.height()

    @checked
    def setSheetHeight(self : Self, height : float) -> None:
        self._sheet_rect.setHeight(height)
        self.updateSceneRect()
        self.update()
        self.properties.signalChanges("Sheet Height")

    @checked
    def getMargin(self : Self) -> float:
        return self._sheet_margin

    @checked
    def setMargin(self : Self, margin : float) -> None:
        self._sheet_margin = margin
        self.update()
        self.properties.signalChanges("Margin")

    @checked
    def getBorder(self : Self) -> float:
        return self._sheet_border

    @checked
    def setBorder(self : Self, border : float) -> None:
        self._sheet_border = border
        self.update()
        self.properties.signalChanges("Border")
