from typing          import Self, TextIO, TypeVar, cast
from collections.abc import Sequence

from PyQt6.QtGui import QStandardItem, QStandardItemModel

from antlr4                     import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from pyTooling.Decorators import export

from .vhdl_lexer   import vhdl_lexer as vhl
from .vhdl_parser  import vhdl_parser as vhp
from .vhdl_visitor import VhdlVisitor


T = TypeVar("T")


def _item(obj : object) -> QStandardItem:
    return cast(QStandardItem, obj)


def _rows(parent : QStandardItem, cls : type[T]) -> list[T]:
    found : list[T] = []
    for row in range(parent.rowCount()):
        child = parent.child(row)
        if isinstance(child, cls):
            found.append(child)
    return found


def _clear_rows(item : QStandardItem) -> None:
    count = item.rowCount()
    if count:
        item.removeRows(0, count)


def _list(items : Sequence[T] | None) -> list[T]:
    return [] if items is None else list(items)


class VhdlItemWithNameMixin:
    @property
    def name(self) -> str:
        return _item(self).text()

    @name.setter
    def name(self, value: str) -> None:
        _item(self).setText(value)

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
        self  : Self,
        name  : str,
        ports : Sequence[VhdlPort] | None = None,
        notes : str = ""
    ) -> None:
        super().__init__(name)
        self.name = name
        self.notes = notes
        self.ports = _list(ports)

    def addPort(self, port: VhdlPort) -> None:
        self._ports.append(port)

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
    _generics    : list[VhdlGeneric]
    _port_groups : list[VhdlPortGroup]

    def __init__(
        self     : Self,
        name     : str,
        generics : Sequence[VhdlGeneric]              | None = None,
        ports    : Sequence[VhdlPort | VhdlPortGroup] | None = None
    ) -> None:
        super().__init__(name)
        self.name = name
        self.generics = _list(generics)
        self.ports = _list(ports)

    def addGeneric(self, generic: VhdlGeneric) -> None:
        self._generics.append(generic)

    @property
    def generics(self) -> list[VhdlGeneric]:
        return self._generics

    @generics.setter
    def generics(self, items: list[VhdlGeneric]) -> None:
        self._generics = items.copy()

    @property
    def ports(self) -> list[VhdlPort]:
        return [port for group in self.port_groups for port in group.ports]

    @ports.setter
    def ports(self, items: list[VhdlPort | VhdlPortGroup]) -> None:
        self._port_groups = []
        ungrouped_ports = []
        for item in items:
            if isinstance(item, VhdlPort):
                ungrouped_ports.append(item)
            elif isinstance(item, VhdlPortGroup):
                self._port_groups.append(item)
        if ungrouped_ports:
            self._port_groups.insert(0, VhdlPortGroup("", ungrouped_ports))

    def addPortGroup(self, port_group: VhdlPortGroup) -> None:
        self._port_groups.append(port_group)

    @property
    def port_group_names(self) -> list[str]:
        return [port_group.name for port_group in self._port_groups]

    @property
    def port_groups(self) -> list[VhdlPortGroup]:
        return self._port_groups

    def portGroup(self, name: str) -> VhdlPortGroup | None:
        for port_group in self._port_groups:
            if port_group.name == name:
                return port_group
        return None

    def portGroupPorts(self, name: str) -> list[VhdlPort]:
        port_group = self.portGroup(name)
        return port_group.ports if port_group is not None else []

@export
class VhdlComponent(VhdlEntity):
    pass

@export
class VhdlArchitecture(
    QStandardItem,
    VhdlItemWithNameMixin,
    VhdlItemWithComponentsMixin
):
    _entity_name : str        | None
    _entity      : VhdlEntity | None

    def __init__(
        self       : Self,
        name       : str,
        entity     : str | VhdlEntity        | None = None,
        components : Sequence[VhdlComponent] | None = None
    ) -> None:
        super().__init__(name)
        self.name = name
        self.components = _list(components)
        if isinstance(entity, str):
            self.entity_name = entity
        else:
            self.entity = entity

    @property
    def entity_name(self) -> str | None:
        return self._entity_name

    @entity_name.setter
    def entity_name(self, name: str) -> None:
        self._entity_name = name
        self._entity = None

    @property
    def entity(self) -> VhdlEntity | None:
        return self._entity if isinstance(self._entity, VhdlEntity) else None

    @entity.setter
    def entity(self, entity: VhdlEntity | None) -> None:
        self._entity = entity
        if entity is not None:
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
        components : Sequence[VhdlComponent] | None = None
    ) -> None:
        super().__init__(name)
        self.name = name
        self.components = _list(components)

@export
class VhdlContainer(QStandardItem):
    _NAME : str | None = None

    def __init__(self) -> None:
        super().__init__()
        if self._NAME is not None:
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
        return _rows(self._entities, VhdlEntity)

    @entities.setter
    def entities(self : Self, items: list[VhdlEntity]) -> None:
        _clear_rows(self._entities)
        self._entities.appendRows(items)

    def addArchitecture(self : Self, architecture: VhdlArchitecture) -> None:
        self._architectures.appendRow(architecture)

    @property
    def architectures(self : Self) -> list[VhdlArchitecture]:
        return _rows(self._architectures, VhdlArchitecture)

    @architectures.setter
    def architectures(self : Self, items: list[VhdlArchitecture]) -> None:
        _clear_rows(self._architectures)
        self._architectures.appendRows(items)

    def addPackage(self : Self, package: VhdlPackage) -> None:
        self._packages.appendRow(package)

    @property
    def packages(self : Self) -> list[VhdlPackage]:
        return _rows(self._packages, VhdlPackage)

    @packages.setter
    def packages(self : Self, items: list[VhdlPackage]) -> None:
        _clear_rows(self._packages)
        self._packages.appendRows(items)

    def analyze(self : Self) -> None:
        for architecture in self.architectures:
            entity_name = architecture.entity_name
            if architecture.entity is None and entity_name is not None:
                architecture.entity = self.getEntity(entity_name)

    @classmethod
    def fromStream(cls, stream: TextIO) -> 'VhdlDocument':
        from . import VHDLSyntaxError

        class VHDLErrorListener(ErrorListener):
            def syntaxError(
                self            : Self,
                recognizer      : object,
                offendingSymbol : object,
                line            : int,
                column          : int,
                msg             : object,
                e               : BaseException | None,
            ) -> None:
                raise VHDLSyntaxError(
                    f"Syntax error at line {line}, column {column}: {msg}"
                )

        input_stream = InputStream(stream.read())
        lexer = vhl(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = vhp(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(VHDLErrorListener())
        try:
            tree = parser.rule_DesignFile()
        except Exception as e:
            raise VHDLSyntaxError(f"Failed to parse VHDL code: {str(e)}") from e
        visitor = VhdlVisitor()
        document = visitor.visit(tree)
        if not isinstance(document, VhdlDocument):
            raise VHDLSyntaxError("Failed to parse VHDL code")
        document.analyze()
        return document

    @classmethod
    def FromFile(cls, filename: str) -> 'VhdlDocument':
        with open(filename) as file:
            return cls.fromStream(file)
