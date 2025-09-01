from typing import Self, Any

from PyQt6.QtWidgets import QGraphicsItem


class ElementChangeMixin:
    def itemChange(
        self   : QGraphicsItem,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        match change:
            case QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
                if hasattr(self, 'onParentChange'):
                    self.onParentChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
                if hasattr(self, 'onSceneChange'):
                    self.onSceneChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
                if hasattr(self, 'onPositionChange'):
                    self.onPositionChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
                if hasattr(self, "line"):
                    self.line.onSelectionChange(value)
                if hasattr(self, "fill"):
                    self.fill.onSelectionChange(value)
                if hasattr(self, "quill"):
                    self.quill.onSelectionChange(value)
                if hasattr(self, "updateHandlesVisibility"):
                    self.updateHandlesVisibility()
                if hasattr(self, "onSelectionChange"):
                    self.onSelectionChange(value)
        return super().itemChange(change, value)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        if hasattr(self, "line"):
            self.line.onSettingsChange()
        if hasattr(self, "fill"):
            self.fill.onSettingsChange()
        if hasattr(self, "quill"):
            self.quill.onSettingsChange()
        if hasattr(self, "outline"):
            self.outline.onSettingsChange()
        self.onGeometryChange()
