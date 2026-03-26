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
                if hasattr(self, "onSceneChange"):
                    self.onSceneChange(value)
            case self.GraphicsItemChange.ItemParentHasChanged:
                if hasattr(self, "onParentChange"):
                    self.onParentChange(value)
            case self.GraphicsItemChange.ItemScenePositionHasChanged:
                if hasattr(self, "onScenePositionChange"):
                    self.onScenePositionChange(value)
            case self.GraphicsItemChange.ItemPositionHasChanged:
                if hasattr(self, "onPositionChange"):
                    self.onPositionChange(value)
            case self.GraphicsItemChange.ItemRotationHasChanged:
                if hasattr(self, "onRotationChange"):
                    self.onRotationChange(value)
            case self.GraphicsItemChange.ItemSelectedHasChanged:
                if hasattr(self, "lineSelectionChange"):
                    self.lineSelectionChange(value)
                if hasattr(self, "fillSelectionChange"):
                    self.fillSelectionChange(value)
                if hasattr(self, "quillSelectionChange"):
                    self.quillSelectionChange(value)
                if hasattr(self, "onSelectionChange"):
                    self.onSelectionChange(value)
        return super().itemChange(change, value)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        if hasattr(self, "a"):
            if self.a.line is not None:
                self.a.line.onSettingsChange()
            if self.a.fill is not None:
                self.a.fill.onSettingsChange()
            if self.a.quill is not None:
                self.a.quill.onSettingsChange()
        if hasattr(self, "outline"):
            self.outline.onSettingsChange()
        if hasattr(self, "onGeometryChange"):
            self.onGeometryChange()
