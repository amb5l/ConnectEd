from ...drawing.api import DrawingSceneApiMixin

from .add  import DiagramSceneApiAddMixin
from .conn import DiagramSceneApiConnMixin
from .edit import DiagramSceneApiEditMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.symbol import SymbolDefinitionItem, SymbolInstanceItem
    from .. import DiagramScene

class DiagramSceneApiMixin(
    DiagramSceneApiAddMixin,
    DiagramSceneApiConnMixin,
    DiagramSceneApiEditMixin,
    DrawingSceneApiMixin
):
    def symbolInstances(
        self       : "DiagramScene",
        definition : "SymbolDefinitionItem"
    ) -> list["SymbolInstanceItem"]:
        return [
            item for item in self.items()
            if isinstance(item, SymbolInstanceItem)
            and item.definition() is definition
        ]
