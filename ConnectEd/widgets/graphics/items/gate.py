from typing import Self
from enum import Enum

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.types import Direction, DataKind

from ..properties import InherentProperty

from ..painter_path import PainterPath

from .gate_pin import GatePinItem, BufGatePinItem, OrGatePinItem

from .mixin           import PrimaryItemMixin
from .mixin.transform import ItemTransformMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from ..views.drawing import DrawingView


class GateFunc(Enum):
    BUF_INV  = "buffer/inverter"
    AND_NAND = "AND/NAND"
    OR_NOR   = "OR/NOR"
    XOR_XNOR = "XOR/XNOR"


class GateLabelMixin:
    # class attributes
    _PROPERTIES_LABEL = {
        "Label" : InherentProperty(
            kind   = DataKind.STR,
            worthy = lambda self: self.label() != "",
            getter = lambda self: self.label(),
            setter = lambda self, value: self.setLabel(value)
        )
    }

    # instance attributes
    _label : str = ""

    def label(self : Self) -> str:
        return self._label

    @checked
    def setLabel(self : Self, label : str) -> None:
        self._label = label
        if hasattr(self, "properties"):
            self.properties.signalChanges("Label")


class BaseGateItem(
    GateLabelMixin,
    ItemTransformMixin,
    PrimaryItemMixin,
    QGraphicsPathItem
):
    # class attributes
    _PIN_CLS = GatePinItem

    @checked
    def __init__(self : Self, fresh : bool = True) -> None:
        super().__init__()
        self.initItem(fresh)
        self.initPath()

    def settingsName(self : Self) -> str:
        return "Gate"

    def label(self : Self) -> str | None:
        return self._label

    @checked
    def setLabel(self : Self, label : str) -> None:
        self._label = label
        if hasattr(self, "properties"):
            self.properties.signalChanges("Label")

    def initPath(self : Self) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
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


class BufGateItem(BaseGateItem):
    """Buffer/Inverter gate."""

    # class attributes
    _PIN_CLS = BufGatePinItem
    _PROPERTIES_IO = {
        "Output" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.output(),
            setter = lambda self, value: self.setOutput(value)
        ),
        "Input" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.input(),
            setter = lambda self, value: self.setInput(value)
        )
    }
    _PROPERTIES = \
        BaseGateItem._PROPERTIES_LABEL | \
        _PROPERTIES_IO | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        PrimaryItemMixin._PROPERTIES_LINE | \
        PrimaryItemMixin._PROPERTIES_FILL

    def resourcesName(self : Self) -> str:
        return "Gate"

    # instance attributes
    _input  : GatePinItem
    _output : GatePinItem

    @checked
    def __init__(self : Self, fresh : bool = True) -> None:
        super().__init__(fresh)
        self.setOutput()
        self.setInput()

    def initPath(self : Self) -> None:
        """Output pin node is at (0, 0)."""
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

    @checked
    def setOutput(self : Self, level: str = "H") -> None:
        if not hasattr(self, '_output'):
            self._output = self._PIN_CLS(self)
            self._output.setDirection(Direction.OUT)
            self._output.setName("o")
            self._output.setPos(QPointF(-12, 0))
            self._output.setRotation(180)
        self._output.setInverted(level == "L")
        self.properties.signalChanges("Output")

    def input(self : Self) -> str:
        return "" if not hasattr(self, '_input') else \
               "L" if self._input.inverted() else "H"

    @checked
    def setInput(self : Self, level : str = "H") -> None:
        if not hasattr(self, '_input'):
            self._input = self._PIN_CLS(self)
            self._input.setDirection(Direction.IN)
            self._input.setName("i")
            self._input.setPos(QPointF(-28, 0))
        self._input.setInverted(level == "L")
        self.properties.signalChanges("Input")


class LogicGateItem(BaseGateItem):
    """Base class for N:1 logic gates."""

    # class attributes
    _MID_PIN_CLS = GatePinItem  # for extended middle input pin
    _PROPERTIES_IO = {
        "Output" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.output(),
            setter = lambda self, value: self.setOutput(value)
        ),
        "Inputs" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.inputs(),
            setter = lambda self, value: self.setInputs(value)
        )
    }
    _PROPERTIES = \
        BaseGateItem._PROPERTIES_LABEL | \
        _PROPERTIES_IO | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        PrimaryItemMixin._PROPERTIES_LINE | \
        PrimaryItemMixin._PROPERTIES_FILL
    _PEN_CAP_STYLE = Qt.PenCapStyle.RoundCap
    _PEN_JOIN_STYLE = Qt.PenJoinStyle.RoundJoin

    def resourcesName(self : Self) -> str:
        return "GateRound"  # gate pen with round cap and round join

    # instance attributes
    _inputs : list[GatePinItem]
    _output : GatePinItem

    @checked
    def __init__(self : Self, width : int | None = None, fresh : bool = True) -> None:
        super().__init__(fresh)
        if fresh:
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

    @checked
    def setOutput(self : Self, level: str = "H") -> None:
        if not hasattr(self, '_output'):
            self._output = self._PIN_CLS(self)
            self._output.setDirection(Direction.OUT)
            self._output.setName("o")
            self._output.setPos(QPointF(-10, 0))
            self._output.setRotation(180)
        self._output.setInverted(level == "L")
        self.properties.signalChanges("Output")

    def inputs(self : Self) -> str:
        return "" if not hasattr(self, '_inputs') else \
               "".join(["L" if pin.inverted() else "H" for pin in self._inputs])

    @checked
    def setInputs(self : Self, levels : str) -> None:
        w = len(levels)
        if not hasattr(self, '_inputs'):
            self._inputs = []
            for i, level in enumerate(levels):
                pin_cls = self._PIN_CLS
                if (w % 2) and (i == w // 2):
                    pin_cls = self._MID_PIN_CLS
                pin = pin_cls(self)
                pin.setDirection(Direction.IN)
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
        self.properties.signalChanges("Inputs")


class AndGateItem(LogicGateItem):
    _VHDL_OPERATOR = "and"

    def initPath(self : Self) -> None:
        path = PainterPath()
        path.moveTo(-30, -10)
        path.lineTo(-20, -10)
        path.arcSpanTo(-20, 10, -180)
        path.lineTo(-30, 10)
        path.closeSubpath()
        self.setPath(path)


class OrGateItem(LogicGateItem):
    _MID_PIN_CLS = OrGatePinItem
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

    @checked
    def setInputs(self : Self, levels : str) -> None:
        super().setInputs(levels)
        if len(self._inputs) % 2 == 1:  # odd width => center input
            # tweak position of center input
            i = len(self._inputs) // 2
            self._inputs[i].setPos(QPointF(-26, 0))


class XorGateItem(OrGateItem):
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
