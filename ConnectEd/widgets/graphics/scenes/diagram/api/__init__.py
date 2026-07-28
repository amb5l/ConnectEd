from __future__ import annotations

from typing import Self

from ......core.check import checked

from .edit       import DiagramSceneApiEditMixin
from .add        import DiagramSceneApiAddMixin
from .conn       import DiagramSceneApiConnMixin
from .properties import DiagramSceneApiPropertiesMixin
from .util       import DiagramSceneApiUtilMixin

from ..host import asDiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.symbol import SymbolDefinitionItem, SymbolInstanceItem

class DiagramSceneApiMixin(
    DiagramSceneApiEditMixin,
    DiagramSceneApiAddMixin,
    DiagramSceneApiConnMixin,
    DiagramSceneApiPropertiesMixin,
    DiagramSceneApiUtilMixin
):
    @checked
    def symbolInstances(
        self       : Self,
        definition : SymbolDefinitionItem
    ) -> list[SymbolInstanceItem]:
        from ....items.symbol import SymbolInstanceItem
        host = asDiagramScene(self)
        return [
            item for item in host.items()
            if isinstance(item, SymbolInstanceItem)
            and item.definition() is definition
        ]
