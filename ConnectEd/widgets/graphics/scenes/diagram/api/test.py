from PyQt6.QtCore import QPointF

from ......core.check import checked
from ......core.types import Direction, Edge

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiTestMixin:
    @checked
    def test(self : "DiagramScene") -> None:
        """Place a sample block with one pin centred on each edge (dev harness)."""
        p1 = QPointF(100, 100)
        p2 = QPointF(200, 200)
        block = BlockItem(p1, p2)
        block.setLabel("U_test")
        block.setName("TestBlock")
        self.addItems([block], undoable=True)

        centre = 50.0
        for name, direction, edge, offset in (
            ("pin_l", Direction.IN,  Edge.LEFT,   centre),
            ("pin_r", Direction.OUT, Edge.RIGHT,  centre),
            ("pin_t", Direction.IN,  Edge.TOP,    centre),
            ("pin_b", Direction.OUT, Edge.BOTTOM, centre),
        ):
            pin = BlockPinItem()
            pin.setName(name)
            pin.setDirection(direction)
            pin.setLocEdge(edge)
            pin.setLocOffset(offset)
            self.addBlockPin(block, pin, undoable=True)

        self.netlistChanged.emit()
