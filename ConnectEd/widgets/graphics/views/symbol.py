from typing import Self

from ..scenes.symbol import SymbolScene

from .definition import DefinitionView, DefinitionSubWindow


class SymbolView(DefinitionView[SymbolScene]):
    """View for editing a single symbol definition."""

    def scene(self : Self) -> SymbolScene | None:
        if (scene := super().scene()) is None:
            return None
        if not isinstance(scene, SymbolScene):
            raise TypeError("Bad scene")
        return scene


class SymbolSubWindow(DefinitionSubWindow):
    """Subwindow for editing a single symbol definition."""
