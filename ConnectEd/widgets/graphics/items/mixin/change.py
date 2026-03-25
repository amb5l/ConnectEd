from typing import Self, Any

from collections.abc import Callable

from PyQt6.QtWidgets import QGraphicsItem


class ItemChangeMixin:
    _selection_handlers : list[Callable[[bool], None]]

    def initChange(self : Self) -> None:
        self._selection_handlers = []

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
                for handler in self._selection_handlers:
                    handler(value)
                if hasattr(self, "a"):
                    if self.a.line is not None:
                        self.a.line.onSelectionChange(value)
                    if self.a.fill is not None:
                        self.a.fill.onSelectionChange(value)
                    if self.a.quill is not None:
                        self.a.quill.onSelectionChange(value)
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

    def addSelectionHandler(self : Self, handler : Callable[[bool], None]) -> None:
        self._selection_handlers.append(handler)
