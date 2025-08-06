from typing import Self, Optional

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from pyTooling.Decorators import export

from .....core import logger, copy

from ....dialogs.appearance import AppearancePref, AppearancePrefChange
from ....dialogs.properties import PropertiesType

from ...items import ElementMixin, QuillPref, QuillPrefChange, clone

from ...items.base_text import BaseText

from ...items.property_text import PropertyText

from .cmd import cmdSceneElement, cmdSceneElements, \
                 cmdSelectionMixin, cmdAddRemoveMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem



@export
class DrawingSceneApiEditMixin:
    def editCut(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() \
                if isinstance(item, ElementMixin) \
                and item.parentItem() is None]
        if elements:
            copy(elements, pos)
            self.undo_stack.push(cmdDelete(self, elements))
        else:
            logger.warning("No elements selected to cut")

    def editCopy(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() \
                if hasattr(item, "toXml") \
                and item.parentItem() is None]
        if elements:
            copy(elements, pos)
        else:
            logger.warning("No elements selected to copy")

    def editDelete(
        self : "DrawingScene"
    ) -> None:
        """Delete selected elements from the scene."""
        elements = self._selectedTopElements()
        if elements:
            self.undo_stack.push(cmdDelete(self, elements))
        else:
            logger.warning("No elements selected to delete")

    def editSelectArea(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editSelectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editText(
        self       : "DrawingScene",
        element    : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditText(self, element, text, appearance))

    def editPropertyText(
        self       : "DrawingScene",
        element    : PropertyText,
        name       : str,
        value      : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditPropertyText(
            self, element, name, value, appearance
        ))

    def editProperties(
        self    : "DrawingScene",
        element : ElementMixin,
        changes : dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]
    ) -> None:
        self.undo_stack.push(cmdEditProperties(self, element, changes))

    def editAppearance(
        self     : "DrawingScene",
        elements : list[ElementMixin],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))
