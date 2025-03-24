__all__ = ['Drawing']

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem

from ...core    import settings, count
from ...widgets import Extents, Grid


class Drawing(QGraphicsScene):
    name        : str
    extents     : Extents
    grid        : Grid
    wip         : list[QGraphicsItem]

    def __init__(self : 'Drawing', name : str | None = None) -> None:
        super().__init__()
        if name is None:
            name = 'Untitled' + str(count)
        self.name    = name
        self.extents = Extents(settings.defaults.sheet)
        self.grid    = Grid(self.extents)
        self.wip     = []
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.addItem(self.extents)
        self.addItem(self.grid)
