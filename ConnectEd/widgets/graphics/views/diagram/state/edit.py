from typing import Self

from PyQt6.QtCore import QPoint, QPointF

from ......core.check import checked

from ......app import logger

from .....dialogs.items.port_pin import PortPinItemDialog

from ....items.mixin import ItemMixin

from ....items.port      import  PortItem
from ....items.block_pin import BlockPinItem

from ...drawing.state.base import DrawingViewStateBase


class DiagramViewStateEditPort(DrawingViewStateBase):
    STATUS = "Edit Port: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(PortItem)
        if item:
            dialog = PortPinItemDialog("Port", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
        else:
            logger().warning("No port selected")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditBlockPin(DrawingViewStateBase):
    STATUS = "Edit Block Pin: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(BlockPinItem)
        if item and isinstance(item, BlockPinItem):
            dialog = PortPinItemDialog("Block Pin", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
        else:
            logger().warning("No block pin selected")
        self.view.state.go(self.view.stateIdle)
