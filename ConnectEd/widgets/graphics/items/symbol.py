from __future__ import annotations

from typing            import Self
from typing_extensions import override

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsRectItem

from ....core.check import checked
from ....core.defs  import PITCH
from ....core.types import RectHandleId, DataKind

from ..properties        import PropertySpec, PropertiesMixin, propertySpecs

from .part       import PartItemMixin
from .role       import DecorativeItem, FunctionalItem
from .symbol_pin import SymbolPinItem
from .mixin      import ItemMixin

from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.handle       import ItemRectHandlesMixin
from .mixin.edge_loc     import ItemEdgeLocParentMixin
from .mixin.transform    import ItemTransformMixin
from .mixin.change       import ItemChangeMixin
from .mixin.clone        import ItemCloneMixin, _copyPropertyDisplay
from .mixin.xml          import ItemXmlMixin
from .mixin.menu         import ItemMenuMixin


class SymbolBaseItem(
    FunctionalItem,
    ItemEdgeLocParentMixin,
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
    _ORIGIN = RectHandleId.TOP_LEFT
    _PROPERTIES_VHDL = {
        "VHDL Library" : PropertySpec["SymbolBaseItem"](
            kind = DataKind.STR,
            getter = lambda self: self.vhdlLibrary(),
            setter = lambda self, value: self.setVhdlLibrary(value),
            tip = (
                "Library containing the component or entity e.g. 'unisim' "
                "(default is 'work')."
            )
        ),
        "VHDL Package" : PropertySpec["SymbolBaseItem"](
            kind   = DataKind.STR,
            getter = lambda self: self.vhdlPackage(),
            setter = lambda self, value: self.setVhdlPackage(value),
            tip = (
                "Package containing the component e.g. 'vcomponents', "
                "'pkg.subpkg'. Leave empty for entity instantiation."
            )
        ),
        "VHDL Architecture" : PropertySpec["SymbolBaseItem"](
            kind   = DataKind.STR,
            getter = lambda self: self.vhdlArchitecture(),
            setter = lambda self, value: self.setVhdlArchitecture(value),
            tip = (
                "Name of the architecture, required for entity "
                "instantiation. Leave empty for component instantiation."
            )
        )
    }
    _PROPERTIES = PartItemMixin._PROPERTIES_PART | _PROPERTIES_VHDL

    @override
    @classmethod
    def resourcesName(cls : type[Self]) -> str:
        return "Symbol"

    # instance attributes
    _vhdl_library      : str
    _vhdl_package      : str
    _vhdl_architecture : str

    @checked
    def __init__(self : Self, fresh : bool = True) -> None:
        super().__init__()
        self.initPart()
        self.initItem(fresh)
        self._verilog_library          = ""
        self._verilog_name             = ""
        self._vhdl_instantiation_style = ""
        self._vhdl_library             = ""
        self._vhdl_package             = ""
        self._vhdl_name                = ""
        self._vhdl_architecture        = ""

    def width(self : Self) -> float:
        return self.rect().width()

    @checked
    def setWidth(self : Self, width : float) -> None:
        width, _height = self.clipEdgeSize(width, self.height())
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def height(self : Self) -> float:
        return self.rect().height()

    @checked
    def setHeight(self : Self, height : float) -> None:
        _width, height = self.clipEdgeSize(self.width(), height)
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

    def handleRect(self : Self) -> QRectF:
        return self.rect()

    @checked
    def setRect(self : Self, rect : QRectF) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().setRect(rect)
        self.refreshEdgeLocs()
        if hasattr(self, "_handles"):
            self.updateHandlePositions()

    @override
    @checked
    def moveHandleBy(self : Self, id : RectHandleId, d : QPointF) -> None:
        d = self.clipHandleDelta(id, d)
        self.rewriteEdgeOffsets(id, d)
        if id == RectHandleId.MIDDLE_CENTER:
            self.moveBy(d.x(), d.y())
            return
        origin = self.transformOriginPoint()
        p1 = self.pos() - origin
        p2 = p1 + self.rect().bottomRight()
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        match id:
            case RectHandleId.TOP_LEFT:
                x1 += d.x()
                y1 += d.y()
            case RectHandleId.TOP_CENTER:
                y1 += d.y()
            case RectHandleId.TOP_RIGHT:
                y1 += d.y()
                x2 += d.x()
            case RectHandleId.MIDDLE_LEFT:
                x1 += d.x()
            case RectHandleId.MIDDLE_RIGHT:
                x2 += d.x()
            case RectHandleId.BOTTOM_LEFT:
                x1 += d.x()
                y2 += d.y()
            case RectHandleId.BOTTOM_CENTER:
                y2 += d.y()
            case RectHandleId.BOTTOM_RIGHT:
                x2 += d.x()
                y2 += d.y()
            case _:
                raise ValueError(f"Invalid handle: {id}")
        rect = self.rect()
        rect.setSize(QSizeF(
            max(abs(x2 - x1), PITCH),
            max(abs(y2 - y1), PITCH)
        ))
        self.setRect(rect)
        self.setPos(QPointF(min(x1, x2), min(y1, y2)) + self.transformOriginPoint())

    # HDL properties

    def vhdlLibrary(self : Self) -> str:
        return self._vhdl_library

    @checked
    def setVhdlLibrary(self : Self, vhdl_library : str) -> None:
        self._vhdl_library = vhdl_library
        if isinstance(self, PropertiesMixin):
            self.properties["VHDL Library"].notify()

    def vhdlPackage(self : Self) -> str:
        return self._vhdl_package

    @checked
    def setVhdlPackage(self : Self, vhdl_package : str) -> None:
        self._vhdl_package = vhdl_package
        if isinstance(self, PropertiesMixin):
            self.properties["VHDL Package"].notify()

    def vhdlArchitecture(self : Self) -> str:
        return self._vhdl_architecture

    @checked
    def setVhdlArchitecture(self : Self, vhdl_architecture : str) -> None:
        self._vhdl_architecture = vhdl_architecture
        if isinstance(self, PropertiesMixin):
            self.properties["VHDL Architecture"].notify()

    @override
    def _resourceKey(self : Self) -> tuple[bool, bool]:
        from ..scenes.symbol import SymbolScene
        return (isinstance(self.scene(), SymbolScene), self.isSelected())


class SymbolDefinitionItem(SymbolBaseItem):
    # class attributes
    _XML_CHILDREN = frozenset({
        "SymbolPin", "Label", "Line", "Rectangle", "Ellipse", "Polyline", "Text"
    })

    @checked
    def syncFromDefinition(self : Self, item : SymbolDefinitionItem) -> None:
        # remove all current children
        for child in self.childItems():
            child.setParentItem(None)
        # sync shape
        self.setRect(item.rect())
        # copy children
        for child in item.childItems():
            if isinstance(child, SymbolPinItem):
                clone = child.clone()
                clone.setParentItem(self)


class SymbolInstanceItem(ItemTransformMixin, SymbolBaseItem):
    # class attributes
    _PROPERTIES = \
        propertySpecs(SymbolBaseItem._PROPERTIES) | \
        propertySpecs(ItemTransformMixin._PROPERTIES_RECT_ORIGIN) | \
        propertySpecs(ItemTransformMixin._PROPERTIES_NO_ORIGIN)
    _XML_CHILDREN = frozenset({"Label"})

    # instance attributes
    _definition : SymbolDefinitionItem | None = None  # master symbol definition

    def definition(self : Self) -> SymbolDefinitionItem | None:
        return self._definition

    @override
    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        """
        Serialize the instance to XML: properties, position, labels.
        """
        self.toXmlBegin(xw)
        self.toXmlChildren(xw, pins=False)
        self.toXmlEnd(xw)

    def propertySyncInherentFrom(
        self       : Self,
        definition : SymbolDefinitionItem,
    ) -> None:
        """Copy definition inherent values. Placement stays on the instance."""
        skip = {"X", "Y", "Rotation", "MirrorH", "MirrorV", "Origin"}
        for name, source in definition.properties.items():
            if name in skip or not source.isInherent():
                continue
            dest = self.properties.get(name)
            if dest is None or not dest.isInherent():
                continue
            dest.setValue(source.value())

    def propertySyncCustomFrom(
        self       : Self,
        definition : SymbolDefinitionItem,
    ) -> None:
        """Replace instance custom properties with the definition's."""
        for name, prop in list(self.properties.items()):
            if prop.isCustom():
                self.propertyDelete(name)
        for name, source in definition.properties.items():
            if not source.isCustom():
                continue
            added = self.propertyAdd(
                name, source.kind(), source.value(raw = True)
            )
            if added is None:
                continue
            for source_label in definition.labelItems(source):
                dest_label = self.labelAdd(added)
                _copyPropertyDisplay(source_label, dest_label)

    def addMissingLabelsFrom(
        self       : Self,
        definition : SymbolDefinitionItem,
    ) -> None:
        """Add definition labels the instance does not already have."""
        for name, source in definition.properties.items():
            dest = self.properties.get(name)
            if dest is None:
                continue
            source_labels = definition.labelItems(source)
            dest_labels   = self.labelItems(dest)
            for source_label in source_labels[len(dest_labels):]:
                dest_label = self.labelAdd(dest)
                _copyPropertyDisplay(source_label, dest_label)

    def removeLabelsNotIn(
        self       : Self,
        definition : SymbolDefinitionItem,
    ) -> None:
        """Remove instance labels whose property is not on the definition."""
        defined = set(definition.properties)
        for label in list(self.labelItems()):
            name = self.propertyName(label.property())
            if name not in defined:
                self.labelRemove(label)

    def syncLabelsFrom(
        self       : Self,
        definition : SymbolDefinitionItem,
    ) -> None:
        """Reset instance label placement to match the definition."""
        for name, source in definition.properties.items():
            dest = self.properties.get(name)
            if dest is None:
                continue
            source_labels = definition.labelItems(source)
            dest_labels   = self.labelItems(dest)
            for source_label, dest_label in zip(
                source_labels, dest_labels, strict = False
            ):
                _copyPropertyDisplay(source_label, dest_label)

    @checked
    def syncFromDefinition(
        self         : Self,
        definition   : SymbolDefinitionItem,
        *,
        inherent     : bool = False,
        custom       : bool = False,
        label_add    : bool = False,
        label_remove : bool = False,
        label_reset  : bool = False,
        content      : bool = True,
    ) -> None:
        """
        Synchronize this instance with its definition.

        Always rebinds _definition.
        Instance specific inherent properties (position etc) are not touched.

        inherent     — copy definition inherent property values
        custom       — remove custom properties and their labels
        label_add    — add definition labels missing from instance
        label_remove — remove instance labels not in definition
        label_reset  — reset instance label positions to match definition
        content      — reset rectangle, pins and decorations from definition
        """
        def _clearChildren(cls : type) -> None:
            for child in self.childItems():
                if isinstance(child, cls):
                    child.setParentItem(None)
                    scene = self.scene()
                    if scene is not None:
                         scene.removeItem(child)

        def _cloneChildren(cls : type) -> None:
            for child in definition.childItems():
                if isinstance(child, cls) and isinstance(child, ItemCloneMixin):
                    clone = child.clone()
                    clone.setParentItem(self)

        self._definition = definition  # bind to definition
        prev_live = self.propertiesLive()
        self.setPropertiesLive(False)
        try:
            if inherent:
                self.propertySyncInherentFrom(definition)
            if custom:
                self.propertySyncCustomFrom(definition)
            if label_add:
                self.addMissingLabelsFrom(definition)
            if label_remove:
                self.removeLabelsNotIn(definition)
            if label_reset:
                self.syncLabelsFrom(definition)
            if content:
                self.setRect(definition.rect())
                _clearChildren(SymbolPinItem)
                _cloneChildren(SymbolPinItem)
                _clearChildren(DecorativeItem)
                _cloneChildren(DecorativeItem)
            ItemXmlMixin.fromXmlRefresh(self)
        finally:
            self.setPropertiesLive(prev_live)
