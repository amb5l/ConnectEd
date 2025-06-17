from typing import Self, TextIO, Optional

from PyQt6.QtGui import QStandardItem, QStandardItemModel

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from pyTooling.Decorators import export

from .vhdl_lexer   import vhdl_lexer as vhl
from .vhdl_parser  import vhdl_parser as vhp
from .vhdl_visitor import VhdlVisitor


class VhdlItemWithNameMixin:
    @property
    def name(self) -> str:
        return self.text()

    @name.setter
    def name(self, value: str) -> None:
        self.setText(value)

class VhdlItemWithModeMixin:
    _mode : str

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        self._mode = value

class VhdlItemWithDatatypeMixin:
    _datatype : str

    @property
    def datatype(self) -> str:
        return self._datatype

    @datatype.setter
    def datatype(self, value: str) -> None:
        self._datatype = value

class VhdlItemWithDefaultMixin:
    _default : str

    @property
    def default(self) -> str:
        return self._default

    @default.setter
    def default(self, value: str) -> None:
        self._default = value

class VhdlItemWithNotesMixin:
    _notes : str

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = value

class VhdlItemWithComponentsMixin:
    _components : list['VhdlComponent']

    def addComponent(self, component: 'VhdlComponent') -> None:
        self._components.append(component)

    @property
    def components(self) -> list['VhdlComponent']:
        return self._components

    @components.setter
    def components(self, items: list['VhdlComponent']) -> None:
        self._components = items.copy()

@export
class VhdlGeneric(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithDatatypeMixin,
    VhdlItemWithDefaultMixin,
    VhdlItemWithNotesMixin
):
    def __init__(
        self     : Self,
        name     : str,
        datatype : str,
        default  : str = "",
        notes    : str = ""
    ) -> None:
        super().__init__(name)
        self.name = name
        self.datatype = datatype
        self.default = default
        self.notes = notes

@export
class VhdlPort(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithModeMixin,
    VhdlItemWithDatatypeMixin,
    VhdlItemWithDefaultMixin,
    VhdlItemWithNotesMixin
):
    def __init__(
        self     : Self,
        name     : str,
        mode     : str,
        datatype : str,
        default  : str = "",
        notes    : str = ""
    ) -> None:
        super().__init__(name)
        self.name = name
        self.mode = mode
        self.datatype = datatype
        self.default = default
        self.notes = notes

@export
class VhdlPortGroup(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithNotesMixin
):
    _ports : list[VhdlPort]

    def __init__(
        self     : Self,
        name     : str,
        ports    : list[VhdlPort] = [],
        notes    : str = ""
    ) -> None:
        super().__init__(name)
        self.name = name
        self.notes = notes
        self.ports = ports

    @property
    def ports(self) -> list[VhdlPort]:
        return self._ports

    @ports.setter
    def ports(self, items: list[VhdlPort]) -> None:
        self._ports = items.copy()

@export
class VhdlEntity(
    QStandardItem,
    VhdlItemWithNameMixin
):
    _generics : list[VhdlGeneric]
    _ports    : dict[str, VhdlPortGroup]

    def __init__(
        self     : Self,
        name     : str,
        generics : list[VhdlGeneric] = [],
        ports    : list[VhdlPort | VhdlPortGroup] = []
    ) -> None:
        super().__init__(name)
        self.name = name
        self.generics = generics
        self.ports = ports

    @property
    def generics(self) -> list[VhdlGeneric]:
        return self._generics

    @generics.setter
    def generics(self, items: list[VhdlGeneric]) -> None:
        self._generics = items.copy()

    @property
    def ports(self) -> list[VhdlPort]:
        return [port for group in self.portGroups for port in group.ports]

    @ports.setter
    def ports(self, items: list[VhdlPort | VhdlPortGroup]) -> None:
        self._ports = {}
        ungrouped_ports = []
        for item in items:
            if isinstance(item, VhdlPort):
                ungrouped_ports.append(item)
            elif isinstance(item, VhdlPortGroup):
                self._ports[item.name] = item
        if ungrouped_ports:
            self._ports[""] = VhdlPortGroup("", ungrouped_ports)

    @property
    def portGroupNames(self) -> list[str]:
        return list(self._ports.keys())

    @property
    def portGroups(self) -> list[VhdlPortGroup]:
        return list(self._ports.values())

    def portGroup(self, name: str) -> VhdlPortGroup:
        return self._ports[name]

    def portGroupPorts(self, name: str) -> list[VhdlPort]:
        return self.portGroup(name).ports

@export
class VhdlComponent(VhdlEntity):
    pass

@export
class VhdlArchitecture(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithComponentsMixin
):
    _entity_name : Optional[str]
    _entity      : Optional[VhdlEntity]

    def __init__(
        self       : Self,
        name       : str,
        entity     : Optional[str | VhdlEntity] = None,
        components : list[VhdlComponent] = []
    ) -> None:
        super().__init__(name)
        self.name = name
        self.components = components
        if isinstance(entity, str):
            self.entity_name = entity
        else:
            self.entity = entity

    @property
    def entity_name(self) -> str:
        return self._entity_name

    @entity_name.setter
    def entity_name(self, name: str) -> None:
        self._entity_name = name
        self._entity = None

    @property
    def entity(self) -> VhdlEntity | None:
        return self._entity if isinstance(self._entity, VhdlEntity) else None

    @entity.setter
    def entity(self, entity: VhdlEntity) -> None:
        self._entity = entity
        self._entity_name = entity.name

@export
class VhdlPackage(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithComponentsMixin
):
    def __init__(
        self       : Self,
        name       : str,
        components : list[VhdlComponent] = []
    ) -> None:
        super().__init__(name)
        self.name = name
        self.components = components

@export
class VhdlContainer(QStandardItem):
    _NAME = None

    def __init__(self) -> None:
        super().__init__()
        self.setText(self._NAME)

@export
class VhdlEntitiesContainer(VhdlContainer):
    _NAME = "Entities"

@export
class VhdlArchitecturesContainer(VhdlContainer):
    _NAME = "Architectures"

@export
class VhdlPackagesContainer(VhdlContainer):
    _NAME = "Packages"

@export
class VhdlDocument(
    QStandardItemModel,
    VhdlItemWithNameMixin
):
    _entities      : VhdlEntitiesContainer
    _architectures : VhdlArchitecturesContainer
    _packages      : VhdlPackagesContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self._entities = VhdlEntitiesContainer()
        self._architectures = VhdlArchitecturesContainer()
        self._packages = VhdlPackagesContainer()
        self.appendRow(self._entities)
        self.appendRow(self._architectures)
        self.appendRow(self._packages)

    def addEntity(self : Self, entity: VhdlEntity) -> None:
        self._entities.appendRow(entity)

    def getEntity(self : Self, name: str) -> VhdlEntity | None:
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None

    @property
    def entities(self : Self) -> list[VhdlEntity]:
        return [self._entities.child(i) for i in range(self._entities.rowCount())]

    @entities.setter
    def entities(self : Self, items: list[VhdlEntity]) -> None:
        self._entities.clear()
        for item in items:
            self._entities.appendRow(item)

    def addArchitecture(self : Self, architecture: VhdlArchitecture) -> None:
        self._architectures.appendRow(architecture)

    @property
    def architectures(self : Self) -> list[VhdlArchitecture]:
        return [self._architectures.child(i) for i in range(self._architectures.rowCount())]

    @architectures.setter
    def architectures(self : Self, items: list[VhdlArchitecture]) -> None:
        self._architectures.clear()
        for item in items:
            self._architectures.appendRow(item)

    def addPackage(self : Self, package: VhdlPackage) -> None:
        self._packages.appendRow(package)

    @property
    def packages(self : Self) -> list[VhdlPackage]:
        return [self._packages.child(i) for i in range(self._packages.rowCount())]

    @packages.setter
    def packages(self : Self, items: list[VhdlPackage]) -> None:
        self._packages.clear()
        for item in items:
            self._packages.appendRow(item)

    def analyze(self : Self) -> None:
        for architecture in self.architectures:
            if architecture.entity is None:
                architecture.entity = self.getEntity(architecture.entity_name)

    @classmethod
    def fromStream(cls, stream: TextIO) -> 'VhdlDocument':
        from . import VHDLSyntaxError

        class VHDLErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                raise VHDLSyntaxError(f"Syntax error at line {line}, column {column}: {msg}")

        input_stream = InputStream(stream.read())
        lexer = vhl(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = vhp(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(VHDLErrorListener())
        try:
            tree = parser.rule_DesignFile()
        except Exception as e:
            raise VHDLSyntaxError(f"Failed to parse VHDL code: {str(e)}")
        visitor = VhdlVisitor()
        document = visitor.visit(tree)
        document.analyze()
        return document

    @classmethod
    def FromFile(cls, filename: str) -> 'VhdlDocument':
        with open(filename, 'r') as file:
            return cls.fromStream(file)
