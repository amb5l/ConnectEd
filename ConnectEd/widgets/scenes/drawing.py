__all__ = ['DrawingScene']

from typing import Optional

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem

from ...core    import settings, count
from ..items import Extents, Grid, Grip


class DrawingScene(QGraphicsScene):
    # class variables
    SYSTEM_FORBIDDEN_ITEMS : Optional[list[QGraphicsItem]] = [Grip]
    SYSTEM_ALLOWED_ITEMS   : Optional[list[QGraphicsItem]] = [Extents, Grid]
    FORBIDDEN_ITEMS        : Optional[list[QGraphicsItem]] = None # none
    ALLOWED_ITEMS          : Optional[list[QGraphicsItem]] = None # any

    # instance variables
    name        : str
    extents     : Extents
    grid        : Grid
    wip         : list[QGraphicsItem]

    def __init__(self : 'DrawingScene', name : str | None = None) -> None:
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

    def addItem(self, item : QGraphicsItem) -> None:
        if item in self.SYSTEM_FORBIDDEN_ITEMS:
            raise ValueError(f'Item {item} is forbidden')
        if self.FORBIDDEN_ITEMS is not None:
            if item in self.FORBIDDEN_ITEMS:
                if item not in self.SYSTEM_ALLOWED_ITEMS:
                    raise ValueError(f'Item {item} is forbidden')
        if self.ALLOWED_ITEMS is not None:
            if item not in self.ALLOWED_ITEMS:
                if item not in self.SYSTEM_ALLOWED_ITEMS:
                    raise ValueError(f'Item {item} is not allowed')
        super().addItem(item)
