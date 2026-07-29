from typing import Self

from ..scenes.block import BlockScene

from .definition import DefinitionView, DefinitionSubWindow


class BlockView(DefinitionView[BlockScene]):
    """View for editing a single block definition."""

    def scene(self : Self) -> BlockScene | None:
        if (scene := super().scene()) is None:
            return None
        if not isinstance(scene, BlockScene):
            raise TypeError("Bad scene")
        return scene

class BlockSubWindow(DefinitionSubWindow):
    """Subwindow for editing a single block definition."""
