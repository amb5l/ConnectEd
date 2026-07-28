from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import HandleId, RectHandleId, PortHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .port_pin import PortPinArrowItem, PortPinLineItem
from .grip     import GripItem, MoveGripItem, ResizeGripItem

from .mixin.transform import ItemTransformMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class PortArrowItem(PortPinArrowItem):
    def resourcesName(self : Self) -> str:
        return "PortArrow"

class PortItem(ItemTransformMixin, PortPinLineItem):
    # class attributes
    _NODE_POS  = 0
    _ARROW_CLS = PortArrowItem
    _ARROW_POS = PITCH
    _PROPERTIES = \
        PortPinLineItem._PROPERTIES | ItemTransformMixin._PROPERTIES_NO_ORIGIN
    _PROPERTY_TEXTS = \
        {
            "Name" : PropertyTextSpec(
                cleat=PortHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }
    _XML_CHILDREN = frozenset({"PropertyText"})

    @classmethod
    def handleIdType(cls) -> type[PortHandleId]:
        return PortHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.PORT_HANDLE

    @classmethod
    def handleGripType(cls, id : HandleId) -> type[GripItem]:
        return MoveGripItem if id == PortHandleId.NODE else ResizeGripItem

    @checked
    def moveHandleBy(self : Self, _ : PortHandleId, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action(
                "Rotate CW", lambda: view.editRotateCW(items=[self]), shortcut="]"
            ),
            view.action(
                "Rotate CCW", lambda: view.editRotateCCW(items=[self]), shortcut="["
            ),
            view.action("Edit...", view.editPort),
            view.separator(),
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]
