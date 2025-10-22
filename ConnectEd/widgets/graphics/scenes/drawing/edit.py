from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.xml import copy

from ....dialogs.properties import PropertyState

from ...items               import QuillPrefChange, AppearancePrefChange
from ...items.mixin         import ItemMixin
from ...items.base_text     import BaseText
from ...items.property_text import PropertyText

from .cmd import cmdDelete
from .cmd.edit import cmdEditText, cmdEditPropertyText, \
                      cmdEditProperties, cmdEditAppearance

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneApiEditMixin:
    def editCut(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        items = \
            [item for item in self.selectedItems() \
                if isinstance(item, ItemMixin) \
                and item.parentItem() is None]
        if items:
            copy(items, pos)
            self.undo_stack.push(cmdDelete(self, items, self.selectedItems()))
        else:
            logger().warning("No items selected to cut")

    def editCopy(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        items = \
            [item for item in self.selectedItems() \
                if hasattr(item, "toXml") \
                and item.parentItem() is None]
        if items:
            copy(items, pos)
        else:
            logger().warning("No items selected to copy")

    def editDelete(
        self : "DrawingScene"
    ) -> None:
        """Delete selected items from the scene."""
        items = self._selectedTopItems()
        if items:
            self.undo_stack.push(cmdDelete(self, items, self.selectedItems()))
        else:
            logger().warning("No items selected to delete")

    def editSelectArea(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editSelectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editText(
        self       : "DrawingScene",
        item       : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditText(self, item, text, appearance))

    def editPropertyText(
        self       : "DrawingScene",
        item       : PropertyText,
        name       : str,
        value      : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditPropertyText(
            self, item, name, value, appearance
        ))

    def editAppearance(
        self    : "DrawingScene",
        items   : list[ItemMixin],
        changes : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, items, changes))

    def editProperties(
        self    : "DrawingScene",
        item    : ItemMixin,
        changes : dict[str, PropertyState]
    ) -> None:
        self.undo_stack.push(cmdEditProperties(self, item, changes))
