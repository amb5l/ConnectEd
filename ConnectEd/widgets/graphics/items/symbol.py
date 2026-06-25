from typing import Self

from PyQt6.QtCore import QXmlStreamWriter

from ....core.types import DataKind

from PyQt6.QtWidgets import QGraphicsRectItem

from ..properties import PropertiesMixin, InherentProperty

from .part import PartItemMixin

from .role import DecorativeItem, FunctionalItem

from .symbol_pin import SymbolPinItem

from .mixin              import ItemMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.handle       import ItemRectHandlesMixin
from .mixin.transform    import ItemTransformMixin
from .mixin.change       import ItemChangeMixin
from .mixin.clone        import ItemCloneMixin
from .mixin.xml          import ItemXmlMixin
from .mixin.menu         import ItemMenuMixin


class SymbolDefinitionItem(
    FunctionalItem,
    ItemMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemRectHandlesMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    PartItemMixin,
    QGraphicsRectItem
):
    # class attributes
    _PROPERTIES = \
        PartItemMixin._PROPERTIES_PART | \
        {
            "Verilog Library" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.verilogLibrary(),
                setter = lambda self, value: self.setVerilogLibrary(value),
                tip    = "Library where the module is defined (normally for simulation). Used for explanatory comments only."
            ),
            "Verilog Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.verilogName(),
                setter = lambda self, value: self.setVerilogName(value),
                tip    = "Name of the module (optional, overrides 'Name' if specified)."
            ),
            "VHDL Instantiation Style" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.vhdlInstantiationStyle(),
                setter = lambda self, value: self.setVhdlInstantiationStyle(value),
                tip    = "'component' (default if not specified) or 'entity'."
            ),
            "VHDL Library" : InherentProperty(
                kind = DataKind.STR,
                getter = lambda self: self.vhdlLibrary(),
                setter = lambda self, value: self.setVhdlLibrary(value),
                tip = (
                    "Library containing the component or entity e.g. 'unisim' "
                    "(default is 'work')."
                )
            ),
            "VHDL Package" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.vhdlPackage(),
                setter = lambda self, value: self.setVhdlPackage(value),
                tip = (
                    "Package containing the component e.g. 'vcomponents', "
                    "'pkg.subpkg'. Use '.all' suffix here to override the item "
                    "name in the ''use'' clause. "
                )
            ),
            "VHDL Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.vhdlName(),
                setter = lambda self, value: self.setVhdlName(value),
                tip = (
                    "Name of the component or entity (optional, overrides "
                    "'Name' if specified)."
                )
            ),
            "VHDL Architecture" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.vhdlArchitecture(),
                setter = lambda self, value: self.setVhdlArchitecture(value),
                tip = (
                    "Name of the architecture, required for entity "
                    "instantiation."
                )
            ),
            "VHDL Selected Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.vhdlSelectedName(),
                tip = (
                "Selected name e.g. 'library.package.name', "
                "'library.entity(architecture)'"
                )
            )
        }
    _XML_CHILDREN = {
        "SymbolPin", "PropertyText", \
        "Line", "Rectangle", "Ellipse", "Polyline", "Text"
    }

    # instance attributes
    _verilog_library          : str
    _verilog_name             : str
    _vhdl_instantiation_style : str
    _vhdl_library             : str
    _vhdl_package             : str
    _vhdl_name                : str
    _vhdl_architecture        : str

    def resourcesName(self : Self) -> str:
        return "Symbol"

    def __init__(self : Self, fresh : bool = True) -> None:
        super().__init__()
        self.initItem(fresh)
        self.initPart()
        self._verilog_library          = ""
        self._verilog_name             = ""
        self._vhdl_instantiation_style = ""
        self._vhdl_library             = ""
        self._vhdl_package             = ""
        self._vhdl_name                = ""
        self._vhdl_architecture        = ""

    def width(self : Self) -> float:
        return self.rect().width()

    def setWidth(self : Self, width : float) -> None:
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def height(self : Self) -> float:
        return self.rect().height()

    def setHeight(self : Self, height : float) -> None:
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

    # HDL properties

    def verilogLibrary(self : Self) -> str:
        return self._verilog_library

    def setVerilogLibrary(self : Self, verilog_library : str) -> None:
        self._verilog_library = verilog_library
        self.properties.signalChanges("Verilog Library")

    def verilogName(self : Self) -> str:
        return self._verilog_name

    def setVerilogName(self : Self, verilog_name : str) -> None:
        self._verilog_name = verilog_name
        self.properties.signalChanges("Verilog Name")

    def vhdlInstantiationStyle(self : Self) -> str:
        return self._vhdl_instantiation_style

    def setVhdlInstantiationStyle(self : Self, vhdl_instantiation_style : str) -> None:
        self._vhdl_instantiation_style = vhdl_instantiation_style
        self.properties.signalChanges("VHDL Instantiation Style")

    def vhdlLibrary(self : Self) -> str:
        return self._vhdl_library

    def setVhdlLibrary(self : Self, vhdl_library : str) -> None:
        self._vhdl_library = vhdl_library
        self.properties.signalChanges("VHDL Library")

    def vhdlPackage(self : Self) -> str:
        return self._vhdl_package

    def setVhdlPackage(self : Self, vhdl_package : str) -> None:
        self._vhdl_package = vhdl_package
        self.properties.signalChanges("VHDL Package")

    def vhdlName(self : Self) -> str:
        return self._vhdl_name

    def setVhdlName(self : Self, vhdl_name : str) -> None:
        self._vhdl_name = vhdl_name
        self.properties.signalChanges("VHDL Name")

    def vhdlArchitecture(self : Self) -> str:
        return self._vhdl_architecture

    def setVhdlArchitecture(self : Self, vhdl_architecture : str) -> None:
        self._vhdl_architecture = vhdl_architecture
        self.properties.signalChanges("VHDL Architecture")

    def vhdlSelectedName(self : Self) -> str:
        s = self.vhdlName() if self.vhdlName() else self.name()
        if self._vhdl_package:
            s = self._vhdl_package + "." + s
        if self._vhdl_library:
            s = self._vhdl_library + "." + s
        return s

    def _resourceKey(self : Self) -> tuple[bool, bool]:
        from ..scenes.symbol import SymbolScene
        return (isinstance(self.scene(), SymbolScene), self.isSelected())

    def _resourceKeyDefault(self : Self) -> tuple[bool, bool]:
        return (False, False)


class SymbolInstanceItem(ItemTransformMixin, SymbolDefinitionItem):
    # class attributes
    _PROPERTIES = \
        SymbolDefinitionItem._PROPERTIES | \
        ItemTransformMixin._PROPERTIES_NO_ORIGIN
    _XML_CHILDREN = {"PropertyText"}

    # instance attributes
    _definition : SymbolDefinitionItem | None = None  # master symbol definition

    def definition(self : Self) -> SymbolDefinitionItem | None:
        return self._definition

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        """
        Serialize the instance to XML: properties, position, property texts.
        """
        self.toXmlBegin(xw)
        self.toXmlChildren(xw, pins=False)
        self.toXmlEnd(xw)

    def sync(
        self,
        definition  : SymbolDefinitionItem,
        *,
        inherent    : bool = False,
        custom      : bool = False,
        text_add    : bool = False,
        text_remove : bool = False,
        text_reset  : bool = False,
        content     : bool = True,
    ) -> None:
        """
        Synchronize this instance with its definition.

        Always rebinds _definition.
        Instance specific inherent properties (position etc) are not touched.

        inherent    — copy definition inherent property values
        custom      — remove custom properties and their texts
        text_add    — add definition property texts missing from instance
        text_remove — remove instance property texts not in definition
        text_reset  — reset instance property text positions to match definition
        content     — reset rectangle, pins and decorations from definition
        """
        def _clearChildren(cls : type) -> None:
            for child in self.childItems():
                if isinstance(child, cls):
                    child.setParentItem(None)
                    if self.scene() is not None:
                         self.scene().removeItem(child)

        def _cloneChildren(cls : type) -> None:
            for child in definition.childItems():
                if isinstance(child, cls) and isinstance(child, ItemCloneMixin):
                    clone = child.clone()
                    clone.setParentItem(self)

        self._definition = definition  # bind to definition
        prev_live = self.live()
        self.setLive(False)
        try:
            if inherent:
                self.properties.syncInherentFrom(definition.properties)
            if custom:
                self.properties.syncCustomFrom(definition.properties)
            if text_add:
                self.properties.addMissingTextsFrom(definition.properties)
            if text_remove:
                self.properties.removeTextsNotIn(definition.properties)
            if text_reset:
                self.properties.syncTextFrom(definition.properties)
            if content:
                self.setRect(definition.rect())
                _clearChildren(SymbolPinItem)
                _cloneChildren(SymbolPinItem)
                _clearChildren(DecorativeItem)
                _cloneChildren(DecorativeItem)
            ItemXmlMixin.fromXmlRefresh(self)
        finally:
            self.setLive(prev_live)