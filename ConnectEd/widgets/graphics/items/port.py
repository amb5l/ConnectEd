from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import RectHandleId, PortHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .role import FunctionalItem

from .port_pin import PortPinArrowItem, PortPinLineItem

from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class PortArrowItem(PortPinArrowItem):
    def resourcesName(self : Self) -> str:
        return "PortArrow"

class PortItem(
    FunctionalItem,
    ItemTransformMixin,
    ItemHandlesMixin[PortHandleId],
    PortPinLineItem
):
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

    @classmethod
    def handleIdType(cls) -> type[PortHandleId]:
        return PortHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.PORT_HANDLE

    @checked
    def moveHandleBy(self : Self, _ : PortHandleId, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        return [
            view.action(
                "Rotate CW", lambda: view.ui.editRotateCW([self]), shortcut="]"
            ),
            view.action(
                "Rotate CCW", lambda: view.ui.editRotateCCW([self]), shortcut="["
            ),
            view.action("Edit...", view.ui.editPort),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
