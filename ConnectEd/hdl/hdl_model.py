from enum   import Enum
from typing import Optional, Iterable, Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QStandardItemModel

from pyTooling.Decorators import export

from .vhdl import VhdlDocument


@export
class HdlDirection(Enum):
    INPUT  = "INPUT"
    OUTPUT = "OUTPUT"
    BIDIR  = "BIDIR"


@export
class HdlItemWithNameMixin:
    """Mixin for items with a name."""

    @property
    def name(self) -> str:
        return self.text()

    @name.setter
    def name(self, name: HdlDirection) -> None:
        self.setText(name)


@export
class HdlItemWithDirectionMixin:
    """Mixin for items with a direction."""

    _direction : HdlDirection

    @property
    def direction(self) -> str:
        return self._direction

    @direction.setter
    def direction(self, direction: HdlDirection) -> None:
        self._direction = direction


@export
class HdlItemWithDatatypeMixin:
    """Mixin for items with a datatype."""

    _datatype : str

    @property
    def datatype(self) -> str:
        return self._datatype

    @datatype.setter
    def datatype(self, datatype: str) -> None:
        self._datatype = datatype


@export
class HdlItemWithDefaultMixin:
    """Mixin for items with a default value."""

    _default : str

    @property
    def default(self) -> str:
        return self._default

    @default.setter
    def default(self, default: str) -> None:
        self._default = default


@export
class HdlItemWithNotesMixin:
    """Mixin for items with notes."""

    _notes : str

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, notes: str) -> None:
        self._notes = notes


@export
class HdlParameter(
    QStandardItem,
    HdlItemWithNameMixin,
    HdlItemWithDatatypeMixin,
    HdlItemWithDefaultMixin,
    HdlItemWithNotesMixin
):
    """Represents a block parameter."""

    def __init__(
        self       : Self,
        name       : str,
        datatype   : str,
        expression : str,
        notes      : str = ""
    ) -> None:
        super().__init__()
        self.name = name
        self.datatype = datatype
        self.default = expression
        self.notes = notes

    def data(self, role: int) -> Optional[str]:
        index = self.index()
        column = index.column() if index.isValid() else 0
        if role == Qt.ItemDataRole.DisplayRole:
            match column:
                case 0: return self.text()
                case 1: return self._datatype
                case 2: return self._default
                case 3: return self._notes
                case _: return None
        return super().data(role)

    def setData(self, value: str, role: int) -> bool:
        index = self.index()
        column = index.column() if index.isValid() else 0

        if role == Qt.ItemDataRole.isplayRole:
            match column:
                case 0: self.setText(value)
                case 1: self._datatype = value
                case 2: self._default = value
                case 3: self._notes = value
                case _: return False
        return super().setData(value, role)


@export
class HdlPortOrPin(
    QStandardItem,
    HdlItemWithNameMixin,
    HdlItemWithDirectionMixin,
    HdlItemWithDatatypeMixin,
    HdlItemWithNotesMixin
):
    """Base class for ports and pins."""

    def __init__(
        self      : Self,
        name      : str,
        direction : HdlDirection,
        datatype  : str,
        notes     : str = ""
    ) -> None:
        super().__init__()
        self.name = name
        self.direction = direction
        self.datatype = datatype
        self.notes = notes

    def data(self, role: int) -> Optional[str]:
        index = self.index()
        column = index.column() if index.isValid() else 0
        if role == Qt.ItemDataRole.DisplayRole:
            match column:
                case 0: return self.text()
                case 1: return self._mode
                case 2: return self._datatype
                case 3: return self._notes
        return None

    def setData(self, value: str, role: int) -> bool:
        index = self.index()
        column = index.column() if index.isValid() else 0

        if role == Qt.ItemDataRole.DisplayRole:
            match column:
                case 0: self.setText(value)
                case 1: self._mode = value
                case 2: self._datatype = value
                case 3: self._notes = value
                case _: return False
        return super().setData(value, role)

@export
class HdlPort(HdlPortOrPin):
    """Represents a diagram (top entity/module) port."""

    pass


@export
class HdlPortGroup(QStandardItem, HdlItemWithNameMixin, HdlItemWithNotesMixin):
    """Represents a diagram port group."""

    def __init__(
        self  : Self,
        name  : str,
        ports : Iterable[HdlPort] = [],
        notes : str = ""
    ) -> None:
        super().__init__()
        self.name = name
        self.appendRows(ports)
        self.notes = notes

@export
class HdlPin(HdlPortOrPin):
    """Represents a block pin."""

    pass


@export
class HdlPinGroup(QStandardItem, HdlItemWithNameMixin, HdlItemWithNotesMixin):
    """Represents a block pin group."""

    def __init__(
        self  : Self,
        name  : str,
        pins  : Iterable[HdlPin] = [],
        notes : str = ""
    ) -> None:
        super().__init__()
        self.name = name
        self.appendRows(pins)
        self.notes = notes

    @property
    def pins(self) -> list[HdlPin]:
        return [self.child(row) for row in range(self.rowCount())]


@export
class HdlContainer(QStandardItem):
    """Base class for containers."""

    _NAME = None

    def __init__(self, items: Iterable[QStandardItem] = []):
        super().__init__()
        if self._NAME is not None:
            self.setText(self._NAME)
        else:
            raise ValueError("HdlContainer._NAME is not set")
        self.appendRows(items)


@export
class HdlParameterContainer(HdlContainer):
    """A container for parameters."""
    _NAME = "Parameters"


@export
class HdlPinContainer(HdlContainer):
    """A container for pins."""

    _NAME = "Pins"


@export
class HdlPinGroupContainer(HdlContainer):
    """A container for pin groups."""

    _NAME = "Pin Groups"


@export
class HdlBlock(QStandardItem, HdlItemWithNameMixin, HdlItemWithNotesMixin):
    """An HdlBlock represents a diagram block or symbol."""

    _parameters : HdlParameterContainer
    _pins       : HdlPinContainer
    _pin_groups : HdlPinGroupContainer

    def __init__(
        self       : Self,
        name       : str,
        parameters : Iterable[HdlParameter] = [],
        pins       : Iterable[HdlPin] = [],
        pin_groups : Iterable[HdlPinGroup] = [],
        notes      : str = ""
    ) -> None:
        super().__init__()
        self.name = name
        self._parameters = HdlParameterContainer(parameters)
        self._pins = HdlPinContainer(pins)
        self._pin_groups = HdlPinGroupContainer(pin_groups)
        self.notes = notes

    @property
    def parameters(self) -> list[HdlParameter]:
        return [self._parameters.child(row) for row in range(self._parameters.rowCount())]

    @parameters.setter
    def parameters(self, value: list[HdlParameter]) -> None:
        self._parameters.clear()
        self._parameters.appendRows(value)

    def addParameter(self, parameter: HdlParameter) -> None:
        self._parameters.appendRow(parameter)

    @property
    def pins(self) -> list[HdlPin]:
        return [self._pins.child(row) for row in range(self._pins.rowCount())]

    @pins.setter
    def pins(self, value: list[HdlPin]) -> None:
        self._pins.clear()
        self._pins.appendRows(value)

    def addPin(self, pin: HdlPin) -> None:
        self._pins.appendRow(pin)

    @property
    def pinGroups(self) -> list[HdlPinGroup]:
        return [self._pin_groups.child(row) for row in range(self._pin_groups.rowCount())]

    @pinGroups.setter
    def pinGroups(self, value: list[HdlPinGroup]) -> None:
        self._pin_groups.clear()
        self._pin_groups.appendRows(value)

    def addPinGroup(self, pin_group: HdlPinGroup) -> None:
        self._pin_groups.appendRow(pin_group)

    def pinGroup(self, name: str) -> list[HdlPin]:
        for row in range(self._pin_groups.rowCount()):
            pin_group = self._pin_groups.child(row)
            if pin_group.text() == name:
                pins = []
                for child_row in range(pin_group.rowCount()):
                    child = pin_group.child(child_row)
                    if isinstance(child, HdlPin):
                        pins.append(child)
                return pins
        return []


@export
class HdlGate(QStandardItem, HdlItemWithNameMixin, HdlItemWithNotesMixin):
    """An HdlGate represents a simple combinatorial function."""

    _pins       : HdlPinContainer

    def __init__(
        self       : Self,
        name       : str,
        notes      : str = "",
        pins       : Iterable[HdlPin] = []
    ):
        super().__init__()
        self.name = name
        self.notes = notes
        for pin in pins:
            self.appendRow(pin)


@export
class HdlNet(
    QStandardItem,
    HdlItemWithNameMixin,
    HdlItemWithDatatypeMixin,
    HdlItemWithNotesMixin
):
    """Represents a net."""

    _output   : HdlPortOrPin
    _inputs   : list[HdlPortOrPin]

    def __init__(
        self     : Self,
        name     : str,
        datatype : str,
        notes    : str = "",
        output   : Optional[HdlPortOrPin] = None,
        inputs   : Iterable[HdlPortOrPin] = []
    ) -> None:
        super().__init__()
        self.setText(name)
        self._datatype = datatype
        self._notes = notes
        self._output = output
        self._inputs = inputs


@export
class HdlNetGroup(QStandardItem, HdlItemWithNameMixin, HdlItemWithNotesMixin):
    """Represents a net group."""

    def __init__(
        self  : Self,
        name  : str,
        notes : str = "",
        nets  : Iterable[HdlNet] = []
    ) -> None:
        super().__init__()
        self.name = name
        self.notes = notes
        for net in nets:
            self.appendRow(net)


@export
class HdlPortGroupContainer(HdlContainer):
    """A container for port groups."""

    _NAME = "Port Groups"


@export
class HdlNetGroupContainer(HdlContainer):
    """A container for net groups."""

    _NAME = "Net Groups"


@export
class HdlBlockContainer(HdlContainer):
    """A container for blocks."""

    _NAME = "Blocks"


@export
class HdlCollection(QStandardItemModel):
    """
    Represents a collection of HDL objects - part or all of a diagram,
    or an (importable) set of blocks.
    """

    _blocks      : HdlBlockContainer
    _port_groups : HdlPortGroupContainer
    _net_groups  : HdlNetGroupContainer

    def __init__(
        self        : Self,
        blocks      : Iterable[HdlBlock] = [],
        port_groups : Iterable[HdlPortGroup] = [],
        net_groups  : Iterable[HdlNetGroup] = []
    ) -> None:
        super().__init__()
        self.appendRows(blocks)

    def addBlock(self, block: HdlBlock) -> None:
        self._blocks.appendRow(block)

    @property
    def blocks(self) -> list[HdlBlock]:
        return [self._blocks.child(row) for row in range(self._blocks.rowCount())]

    @blocks.setter
    def blocks(self, value: list[HdlBlock]) -> None:
        self._blocks.clear()
        self._blocks.appendRows(value)

    def addPortGroup(self, port_group: HdlPortGroup) -> None:
        self._port_groups.appendRow(port_group)

    @property
    def port_groups(self) -> list[HdlPortGroup]:
        return [self._port_groups.child(row) for row in range(self._port_groups.rowCount())]

    @port_groups.setter
    def port_groups(self, value: list[HdlPortGroup]) -> None:
        self._port_groups.clear()
        self._port_groups.appendRows(value)

    def addNetGroup(self, net_group: HdlNetGroup) -> None:
        self._net_groups.appendRow(net_group)

    @property
    def net_groups(self) -> list[HdlNetGroup]:
        return [self._net_groups.child(row) for row in range(self._net_groups.rowCount())]

    @net_groups.setter
    def net_groups(self, value: list[HdlNetGroup]) -> None:
        self._net_groups.clear()
        self._net_groups.appendRows(value)

#    @classmethod
#    def fromVhdlDocument(cls, vhdl_document: VhdlDocument) -> Self:
#        for vhdl_entity in vhdl_document.entities:
#            hdl_block = HdlBlock(vhdl_entity.name)
#            for vhdl_port_group in vhdl_entity.port_groups:
#                if vhdl_port_group.name: # named group of ports
#                    hdl_port_group = HdlPortGroup(
#                        name=vhdl_port_group.name,
#                        notes=vhdl_port_group.notes
#                    )
#                    for vhdl_port in vhdl_port_group.ports:
#                        match vhdl_port.mode:
#                            case "in"    : direction = HdlDirection.INPUT
#                            case "out"   : direction = HdlDirection.OUTPUT
#                            case "inout" : direction = HdlDirection.BIDIR
#                            case _       : direction = HdlDirection.BIDIR
#                        match vh
#                        hdl_port = HdlPort(
#                            name=vhdl_port.name,
#                            direction=direction,
#                            datatype=vhdl_port.datatype,
#                            notes=vhdl_port.notes
#                        )
#                        hdl_port_group.appendRow(hdl_port)
#                else: # ungrouped ports