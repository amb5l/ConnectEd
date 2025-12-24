from typing import Self
from enum import Enum

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from ..painter_path import PainterPath

from . import SignalDirection

from .gate_pin import GatePin

from .mixin            import ItemMixin
from .mixin.pos_rot    import ItemPosRotMixin
from .mixin.paint      import ItemPaintMixin
from .mixin.line       import ItemLineMixin
from .mixin.fill       import ItemFillMixin
from .mixin.change     import ItemChangeMixin
from .mixin.clone      import ItemCloneMixin
from .mixin.xml        import ItemXmlMixin
from .mixin.menu       import ItemMenuMixin

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
    ItemPosRotMixin,
    ItemPaintMixin,
    ItemLineMixin,
    ItemFillMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsPathItem
):
    # class attributes
    _PROPERTY_SPECS_LABEL = {
        "Label" : PropertySpec(
            getter = lambda self: self._label,
            setter = lambda self, value: setattr(self, "_label", value)
        )
    }

    # instance attributes
    _label  : str

    def __init__(self : Self, bare : bool = False) -> None:
        self._label = ""
        super().__init__()
        self.initItem(bare)
        self.initPath()

    def settingsName(self : Self) -> str:
        return "Gate"

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

    # class attributes
    _PROPERTY_SPECS_IO = {
        "Output" : PropertySpec(
            getter = lambda self: self.output(),
            setter = lambda self, value: self.setOutput(value)
        ),
        "Input" : PropertySpec(
            getter = lambda self: self.input(),
            setter = lambda self, value: self.setInput(value)
        )
    }
    _PROPERTY_SPECS = \
        BaseGate._PROPERTY_SPECS_LABEL | \
        _PROPERTY_SPECS_IO | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        ItemLineMixin._PROPERTY_SPECS_LINE | \
        ItemFillMixin._PROPERTY_SPECS_FILL

    # instance attributes
    _input  : GatePin
    _output : GatePin

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__(bare)
        self.setOutput()
        self.setInput()

    def initPath(self : Self) -> None:
        path = PainterPath()
        path.moveTo(-28, -8)
        path.lineTo(-12, 0)
        path.lineTo(-28, 8)
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
        label = self.label()
        if label:
            s += f"{label}: "
        # output net
        s += f"{scene.getPinNetName(self._output)} <= "
        # inversion
        if self._output.inverted() != self._input.inverted():
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
        label = self.label()
        if label:
            s += f"{label}: "
        # always @(*) begin
        s += "always @(*) begin\n"
        # output net
        s += f"    {scene.getPinNetName(self._output)} = "
        # inversion
        s += "~" if self._output.inverted() != self._input.inverted() else ""
        # input net
        s += scene.getPinNetName(self._input)
        # semicolon
        s += ";\n"
        # end
        s += "end\n"
        return s

    def output(self : Self) -> str:
        return "" if not hasattr(self, '_output') else \
               "L" if self._output.inverted() else "H"

    def setOutput(self : Self, level: str = "H") -> None:
        if not hasattr(self, '_output'):
            self._output = GatePin(self)
            self._output.setDirection(SignalDirection.OUT)
            self._output.setName("o")
            self._output.setPos(QPointF(-12, 0))
            self._output.setLength(12)
            self._output.setRotation(180)
        self._output.setInverted(level == "L")

    def input(self : Self) -> str:
        return "" if not hasattr(self, '_input') else \
               "L" if self._input.inverted() else "H"

    def setInput(self : Self, level : str = "H") -> None:
        if not hasattr(self, '_input'):
            self._input = GatePin(self)
            self._input.setDirection(SignalDirection.IN)
            self._input.setName("i")
            self._input.setPos(QPointF(-28, 0))
            self._input.setLength(12)
        self._input.setInverted(level == "L")


class Gate(BaseGate):
    """Base class for N:1 logic gates."""

    # class attributes
    _PROPERTY_SPECS_IO = {
        "Output" : PropertySpec(
            getter = lambda self: self.output(),
            setter = lambda self, value: self.setOutput(value)
        ),
        "Inputs" : PropertySpec(
            getter = lambda self: self.inputs(),
            setter = lambda self, value: self.setInputs(value)
        )
    }
    _PROPERTY_SPECS = \
        BaseGate._PROPERTY_SPECS_LABEL | \
        _PROPERTY_SPECS_IO | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        ItemLineMixin._PROPERTY_SPECS_LINE | \
        ItemFillMixin._PROPERTY_SPECS_FILL

    # instance attributes
    _inputs : list[GatePin]
    _output : GatePin

    def __init__(self : Self, width : int | None = None, bare : bool = False) -> None:
        super().__init__(bare)
        if not bare:
            self.setOutput()
            if width is not None:
                self.setInputs("H" * width)

    def toVhdl(self : Self) -> str:
        """
        Build concurrent assignment VHDL code:
        label: o <= i1 and not i2 and i3 ...
        """
        scene : "DrawingScene" = self.scene()
        s = ""
        # label (optional)
        label = self.label()
        if label:
            s += f"{label}: "
        # output net
        output_net_name = scene.getPinNetName(self._output)
        s += f"{output_net_name} <= "
        # output inversion - open parenthesis
        if self._output.inverted():
            s += "not ("
        # 2 or more inputs
        for n, input_pin in enumerate(self._inputs):
            net_name = scene.getPinNetName(input_pin)
            s += f" {self._VHDL_OPERATOR} " if n > 0 else ""
            s += f"{('not ' if input_pin.inverted() else '')}{net_name}"
        # semicolon
        s += " ;"
        # output inversion - close parenthesis
        if self._output.inverted():
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
        label = self.label()
        if label:
            s += f"{label}: "
        # always @(*) begin
        s += "always @(*) begin\n"
        # output net
        output_net_name = scene.getPinNetName(self._output)
        s += f"    {output_net_name} = "
        # output inversion - open parenthesis
        if self._output.inverted():
            s += "~("
        # 2 or more inputs
        for n, input_pin in enumerate(self._inputs):
            net_name = scene.getPinNetName(input_pin)
            s += f" {self._VLOG_OPERATOR} " if n > 0 else ""
            s += f"{('~' if input_pin.inverted() else '')}{net_name}"
        # output inversion - close parenthesis
        if self._output.inverted():
            s += ")"
        # semicolon
        s += ";\n"
        # end
        s += "end\n"
        return s

    def output(self : Self) -> str:
        return "" if not hasattr(self, '_output') else \
               "L" if self._output.inverted() else "H"

    def setOutput(self : Self, level: str = "H") -> None:
        if not hasattr(self, '_output'):
            self._output = GatePin(self)
            self._output.setDirection(SignalDirection.OUT)
            self._output.setName("o")
            self._output.setPos(QPointF(-10, 0))
            self._output.setRotation(180)
        self._output.setInverted(level == "L")

    def inputs(self : Self) -> str:
        return "" if not hasattr(self, '_inputs') else \
               "".join(["L" if pin.inverted() else "H" for pin in self._inputs])

    def setInputs(self : Self, levels : str) -> None:
        w = len(levels)
        if not hasattr(self, '_inputs'):
            self._inputs = []
            for i, level in enumerate(levels):
                pin = GatePin(self)
                pin.setDirection(SignalDirection.IN)
                pin.setName(f"i{i+1}")
                a = 0 if w % 2 == 1 or i < w // 2 else 1 # skip/don't center
                y = 10 * (-(w // 2) + i + a)
                pin.setPos(QPointF(-30, y))
                pin.setInverted(level == "L")
                self._inputs.append(pin)
            if w > 3:
                # widen gate input side
                path = self.path()
                y = 10 * (w // 2)
                path.moveTo(-30, -y)
                path.lineTo(-30, -10)
                path.moveTo(-30, y)
                path.lineTo(-30, 10)
                self.setPath(path)


class AndGate(Gate):
    _VHDL_OPERATOR = "and"

    def initPath(self : Self) -> None:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-20, -10)
        path.arcSpanTo(-20, 10, -180)
        path.lineTo(-30, 10)
        path.closeSubpath()
        self.setPath(path)


class OrGate(Gate):
    _VHDL_OPERATOR = "or"

    def initPath(self : Self) -> None:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-26, -10)
        path.arcSpanTo(-10, 0, -60)
        path.arcSpanTo(-26, 10, -60)
        path.lineTo(-30, 10)
        path.arcSagittaTo(-30, -10, 4)
        path.closeSubpath()
        self.setPath(path)

    def setInputs(self : Self, levels : str) -> None:
        super().setInputs(levels)
        if len(self._inputs) % 2 == 1:  # odd width => center input
            # tweak position and length of center input
            i = len(self._inputs) // 2
            self._inputs[i].setPos(QPointF(-26, 0))
            self._inputs[i].setLength(14)


class XorGate(OrGate):
    _VHDL_OPERATOR = "xor"

    def initPath(self : Self) -> None:
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
        self.setPath(path)
