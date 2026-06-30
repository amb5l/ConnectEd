from __future__ import annotations

from typing import Self

from ......core.check import checked

from .edit       import DiagramSceneApiEditMixin
from .add        import DiagramSceneApiAddMixin
from .conn       import DiagramSceneApiConnMixin
from .properties import DiagramSceneApiPropertiesMixin
from .util       import DiagramSceneApiUtilMixin

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
        from .. import DiagramScene
        from ....items.symbol import SymbolDefinitionItem, SymbolInstanceItem
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        return [
            item for item in self.items()
            if isinstance(item, SymbolInstanceItem)
            and item.definition() is definition
        ]
