from typing import Self
from enum import Enum

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ..painter_path import PainterPath

from . import SignalDirection

from .gate_pin import GatePin

from .mixin        import ItemMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.line   import ItemLineMixin
from .mixin.fill   import ItemFillMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from ..views.drawing import DrawingView


class GateFunc(Enum):
    BUF_INV  = "buffer/inverter"
    AND_NAND = "AND/NAND"
    OR_NOR   = "OR/NOR"
    XOR_XNOR = "XOR/XNOR"


class BaseGate(
    ItemMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemPaintMixin,
    ItemLineMixin,
    ItemFillMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    # class attributes
    _SETTINGS_NAME = "Gate"

    # instance attributes
    _label  : str | None

    def __init__(self : Self) -> None:
        self._label = None  # TODO support labels via properties
        super().__init__()
        self.initItem()
        self.initPath()

    @property
    def label(self : Self) -> str | None:
        return self._label

    def initPath(self : Self) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Rotate CW", lambda: view.ui.editRotateCW([self]), shortcut="]"
            ),
            view.action(
                "Rotate CCW", lambda: view.ui.editRotateCCW([self]), shortcut="["
            ),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
        ]


class BufGate(BaseGate):
    """Buffer/Inverter gate."""

    # instance attributes
    _input  : GatePin
    _output : GatePin

    def __init__(self : Self) -> None:
        super().__init__()
        self._input = GatePin(self)
        self._input.direction = SignalDirection.IN
        self._input.name = "i"
        self._input.setPos(QPointF(-30, 0))
        self._output = GatePin(self)
        self._output.direction = SignalDirection.OUT
        self._output.name = "o"
        self._output.setPos(QPointF(-10, 0))
        self._output.setRotation(180)

    def initPath(self : Self) -> None:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-10, 0)
        path.lineTo(-30, 10)
        path.closeSubpath()
        self.setPath(path)

    def toVhdl(self : Self) -> str:
        """
        Build concurrent assignment VHDL code:
        label: o <= not i1
        """
        scene : "DrawingScene" = self.scene()
        s = ""
        # label (optional)
        label = self.label
        if label:
            s += f"{label}: "
        # output net
        s += f"{scene.getPinNetName(self._output)} <= "
        # inversion
        if self._output.inverted != self._input.inverted:
            s += "not "
        # input net
        s += scene.getPinNetName(self._input)
        # semicolon
        s += " ;"
        return s

    def toVlog(self : Self) -> str:
        """
        Build concurrent assignment Verilog code:
        label: always @(*) begin
            o = ~i
        end
        """
        scene : "DrawingScene" = self.scene()
        s = ""
        # label (optional)
        label = self.label
        if label:
            s += f"{label}: "
        # always @(*) begin
        s += "always @(*) begin\n"
        # output net
        s += f"    {scene.getPinNetName(self._output)} = "
        # inversion
        s += "~" if self._output.inverted != self._input.inverted else ""
        # input net
        s += scene.getPinNetName(self._input)
        # semicolon
        s += ";\n"
        # end
        s += "end\n"
        return s


class Gate(BaseGate):
    # instance attributes
    _width  : int
    _inputs : list[GatePin]
    _output : GatePin

    def __init__(self : Self, width : int) -> None:
        self._width = width
        super().__init__()
        # input pins
        self._inputs = []
        for i in range(width):
            pin = GatePin(self)
            pin.direction = SignalDirection.IN
            pin.name = f"i{i+1}"
            a = 0 if width % 2 == 1 or i < width // 2 else 1 # skip/don't center
            y = 10 * (-(width // 2) + i + a)
            pin.setPos(QPointF(-30, y))
            self._inputs.append(pin)
        # output pin
        pin = GatePin(self)
        pin.direction = SignalDirection.OUT
        pin.name = "o"
        pin.setPos(QPointF(-10, 0))
        pin.setRotation(180)
        self._output = pin

    @property
    def width(self : Self) -> int:
        return self._width

    def initPath(self : Self) -> None:
        path = self.gatePath()
        if self._width > 3:
            # widen gate input side
            y = 10 * (self._width // 2)
            path.moveTo(-30, -y)
            path.lineTo(-30, -10)
            path.moveTo(-30, y)
            path.lineTo(-30, 10)
        self.setPath(path)

    def gatePath(self : Self) -> PainterPath:
        raise NotImplementedError("Subclasses must implement this method")

    def toVhdl(self : Self) -> str:
        """
        Build concurrent assignment VHDL code:
        label: o <= i1 and not i2 and i3 ...
        """
        scene : "DrawingScene" = self.scene()
        s = ""
        # label (optional)
        label = self.label
        if label:
            s += f"{label}: "
        # output net
        output_net_name = scene.getPinNetName(self._output)
        s += f"{output_net_name} <= "
        # output inversion - open parenthesis
        if self._output.inverted:
            s += "not ("
        # 2 or more inputs
        for n, input_pin in enumerate(self._inputs):
            net_name = scene.getPinNetName(input_pin)
            s += f" {self._VHDL_OPERATOR} " if n > 0 else ""
            s += f"{('not ' if input_pin.inverted else '')}{net_name}"
        # semicolon
        s += " ;"
        # output inversion - close parenthesis
        if self._output.inverted:
            s += ")"
        return s

    def toVlog(self : Self) -> str:
        """
        Build concurrent assignment Verilog code:
        label: always @(*) begin
            o = i1 & ~i2 & i3 ...
        end
        """
        scene : "DrawingScene" = self.scene()
        s = ""
        # label (optional)
        label = self.label
        if label:
            s += f"{label}: "
        # always @(*) begin
        s += "always @(*) begin\n"
        # output net
        output_net_name = scene.getPinNetName(self._output)
        s += f"    {output_net_name} = "
        # output inversion - open parenthesis
        if self._output.inverted:
            s += "~("
        # 2 or more inputs
        for n, input_pin in enumerate(self._inputs):
            net_name = scene.getPinNetName(input_pin)
            s += f" {self._VLOG_OPERATOR} " if n > 0 else ""
            s += f"{('~' if input_pin.inverted else '')}{net_name}"
        # output inversion - close parenthesis
        if self._output.inverted:
            s += ")"
        # semicolon
        s += ";\n"
        # end
        s += "end\n"
        return s


class AndGate(Gate):
    _VHDL_OPERATOR = "and"

    def gatePath(self : Self) -> PainterPath:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-20, -10)
        path.arcSpanTo(-20, 10, -180)
        path.lineTo(-30, 10)
        path.closeSubpath()
        return path


class OrGate(Gate):
    _VHDL_OPERATOR = "or"

    def __init__(self : Self, width : int = 2) -> None:
        super().__init__(width)
        if self._width % 2 == 1:  # odd width => center input
            # tweak position and length of center input
            i = self._width // 2
            self._inputs[i].setPos(QPointF(-26, 0))
            self._inputs[i].setLength(14)

    def gatePath(self : Self) -> PainterPath:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-26, -10)
        path.arcSpanTo(-10, 0, -60)
        path.arcSpanTo(-26, 10, -60)
        path.lineTo(-30, 10)
        path.arcSagittaTo(-30, -10, 4)
        path.closeSubpath()
        return path


class XorGate(OrGate):
    _VHDL_OPERATOR = "xor"

    def gatePath(self : Self) -> PainterPath:
        path = PainterPath()
        path.moveTo(-26, -10)
        path.arcSpanTo(-10, 0, -60)
        path.arcSpanTo(-26, 10, -60)
        path.arcSagittaTo(-26, -10, 4)
        path.closeSubpath()
        path.moveTo(-30, -10)
        path.arcSagittaTo(-30, 10, -4)
        path.arcSagittaTo(-30, -10, 4)
        path.closeSubpath()
        return path
