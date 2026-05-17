from typing import Self, Any

from PyQt6.QtWidgets import QGraphicsItem


class ItemChangeMixin:
    def initChange(self : Self) -> None:
        pass

    def itemChange(
        self   : QGraphicsItem,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        match change:
            case self.GraphicsItemChange.ItemSceneHasChanged:
                if hasattr(self, "onSceneChanged"):
                    self.onSceneChanged(value)
            case self.GraphicsItemChange.ItemParentHasChanged:
                if hasattr(self, "onParentChanged"):
                    self.onParentChanged(value)
            case self.GraphicsItemChange.ItemScenePositionHasChanged:
                if hasattr(self, "onScenePositionChanged"):
                    self.onScenePositionChanged(value)
            case self.GraphicsItemChange.ItemPositionHasChanged:
                if hasattr(self, "onPositionChanged"):
                    self.onPositionChanged(value)
            case self.GraphicsItemChange.ItemRotationHasChanged:
                if hasattr(self, "onRotationChanged"):
                    self.onRotationChanged(value)
            case self.GraphicsItemChange.ItemSelectedHasChanged:
                value = bool(value)
                if hasattr(self, "lineSelectionChange"):
                    self.lineSelectionChange(value)
                if hasattr(self, "fillSelectionChange"):
                    self.fillSelectionChange(value)
                if hasattr(self, "quillSelectionChange"):
                    self.quillSelectionChange(value)
                if hasattr(self, "onSelectionChange"):
                    self.onSelectionChanged(value)
        return super().itemChange(change, value)
