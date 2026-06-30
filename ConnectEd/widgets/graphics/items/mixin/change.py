from typing import Self, Any, cast

from PyQt6.QtWidgets import QGraphicsItem

from .....core.utils import qtItemClass

from ..protocols import (
    OnSceneChangedProtocol,
    OnParentChangedProtocol,
    OnScenePositionChangedProtocol,
    OnPositionChangedProtocol,
    OnRotationChangedProtocol,
    OnSelectionChangedProtocol,
)


class ItemChangeMixin:
    def initChange(self : Self) -> None:
        pass

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        match change:
            case QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
                if isinstance(self, OnSceneChangedProtocol):
                    self.onSceneChanged(value)
            case QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
                if isinstance(self, OnParentChangedProtocol):
                    self.onParentChanged(value)
            case QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
                if isinstance(self, OnScenePositionChangedProtocol):
                    self.onScenePositionChanged(value)
            case QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
                if isinstance(self, OnPositionChangedProtocol):
                    self.onPositionChanged(value)
            case QGraphicsItem.GraphicsItemChange.ItemRotationHasChanged:
                if isinstance(self, OnRotationChangedProtocol):
                    self.onRotationChanged(value)
            case QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
                value = bool(value)
                if isinstance(self, OnSelectionChangedProtocol):
                    self.onSelectionChanged(value)
        return qtItemClass(self).itemChange(
            cast(QGraphicsItem, self), change, value
        )
