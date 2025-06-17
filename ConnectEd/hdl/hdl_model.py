from typing import Optional, Iterable, Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QStandardItemModel

class HdlParameter(QStandardItem):

    _datatype : str
    _default  : str
    _notes    : str

    def __init__(self, name: str, datatype: str, expression, notes: str = "") -> None:
        super().__init__()
        self.setText(name)
        self._datatype = datatype
        self._default = expression
        self._notes = notes

    @property
    def name(self) -> str:
        return self.text()

    @name.setter
    def name(self, value: str) -> None:
        self.setText(value)

    @property
    def datatype(self) -> str:
        return self._datatype

    @datatype.setter
    def datatype(self, value: str) -> None:
        self._datatype = value

    @property
    def default(self) -> str:
        return self._default

    @default.setter
    def default(self, value: str) -> None:
        self._default = value

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = value

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

class HdlPortOrPin(QStandardItem):
    """Base class for ports and pins."""

    _mode     : str
    _datatype : str
    _notes    : str

    def __init__(self, name: str, direction: str, type_: str, notes: str = "") -> None:
        super().__init__()
        self.setText(name)  # Store name in built-in text attribute
        self._mode = direction
        self._datatype = type_
        self._notes = notes

    @property
    def name(self) -> str:
        return self.text()  # Retrieve name from built-in text attribute

    @name.setter
    def name(self, value: str) -> None:
        self.setText(value)  # Store name in built-in text attribute

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        self._mode = value

    @property
    def datatype(self) -> str:
        return self._datatype

    @datatype.setter
    def datatype(self, value: str) -> None:
        self._datatype = value

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = value

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

class HdlPort(HdlPortOrPin):
    """Represents a diagram (top entity/module) port."""
    pass

class HdlPin(HdlPortOrPin):
    """Represents a block pin."""
    pass

class HdlPinGroup(QStandardItem):
    """Represents a block pin group."""

    def __init__(self, name: str, ports: Iterable[HdlPin] = []):
        super().__init__()
        self.setText(name)
        self.appendRows(ports)

    @property
    def pins(self) -> list[HdlPin]:
        return [self.child(row) for row in range(self.rowCount())]

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

class HdlParameterContainer(HdlContainer):
    """A container for parameters."""
    _NAME = "Parameters"

class HdlPinContainer(HdlContainer):
    """A container for pins."""
    _NAME = "Pins"

class HdlPinGroupContainer(HdlContainer):
    """A container for pin groups."""
    _NAME = "Pin Groups"

class HdlBlock(QStandardItem):
    """An HdlBlock represents a diagram block or symbol."""

    _notes      : str
    _parameters : HdlParameterContainer
    _pins       : HdlPinContainer
    _pin_groups : HdlPinGroupContainer

    def __init__(
        self,
        name       : str,
        parameters : Iterable[HdlParameter] = [],
        pins       : Iterable[HdlPin] = [],
        pin_groups : Iterable[HdlPinGroup] = []
    ):
        super().__init__()
        self.setText(name)
        self._parameters = HdlParameterContainer(parameters)
        self._pins = HdlPinContainer(pins)
        self._pin_groups = HdlPinGroupContainer(pin_groups)

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

class HdlGate(QStandardItem):
    """An HdlGate represents a simple combinatorial function."""

    _notes      : str
    _pins       : HdlPinContainer

    def __init__(
        self,
        name       : str,
        parameters : Iterable[HdlParameter] = [],
        pins       : Iterable[HdlPin] = [],
        pin_groups : Iterable[HdlPinGroup] = []
    ):
        super().__init__()
        self.setText(name)
        self._parameters = HdlParameterContainer(parameters)
        self._pins = HdlPinContainer(pins)
        self._pin_groups = HdlPinGroupContainer(pin_groups)

class HdlNet(QStandardItem):
    """Represents a net."""

    _datatype : str
    _notes    : str
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

class HdlNetGroup(QStandardItem):
    """Represents a net group."""
    pass

class HdlModel(QStandardItemModel):
    """Represents a model of an diagram, or (importable) set of blocks."""

    def __init__(self, blocks: Iterable[HdlBlock] = []):
        super().__init__()
        self.appendRows(blocks)
