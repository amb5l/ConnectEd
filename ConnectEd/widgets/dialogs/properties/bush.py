from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QShowEvent

from ...table.item  import TableItem
from ...table.model import TableModel
from ...table.view  import TableView

from ...graphics.properties import PropertiesMixin

from ...graphics.items.mixin import ItemMixin

from .item import PropertiesItem, PropertiesValueItem, PropertiesExpanderItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import StoreProperty, StorePropertyText, OwnerStore


_COLUMNS : dict[str, list[str]] = {
    "Owner" : [
        "Owner ID",
        "Property Expander"
    ],
    "Property" : [
        "Name",
        "Custom",
        "Type",
        "Value",
        "Property Text Expander"
    ],
    "Property Text" : [
        "Visible",
        "Cleat",
        "X",
        "Y",
        "Rotation",
        "Mirror H",
        "Mirror V",
        "Autoflip",
        "Origin",
        "Align H",
        "Align V",
        "Width",
        "Height",
        "Pad Left",
        "Pad Right",
        "Pad Top",
        "Pad Bottom",
        "Color",
        "Font",
        "Size",
        "Bold",
        "Italic",
        "Underline"
    ],
}


class TableRow:
    """
    Dict-shaped list of TableItems.
    """

    _names : list[str]
    _cells : list[TableItem | None]

    def __init__(self, names : list[str]) -> None:
        self._names = names
        self._cells = [None] * len(names)

    def __setitem__(self, name : str, cell : TableItem | None) -> None:
        self._cells[self._names.index(name)] = cell

    def cells(self) -> list[TableItem | None]:
        return self._cells


class PropertiesBushWidget(TableView):
    """
    Compressed tree of owners, properties, and property texts.

    An owner's first row carries its first property and that property's first
    text. Further texts of that property follow on their own rows. The next
    row carries the next property and its first text, and so on. Owner cells
    span every row of that owner. Property cells span the rows of that
    property. Each level has its own columns, so the promoted cells sit side
    by side. Expanders hide the rows after the promoted one.
    Does not support transpose.
    """

    # instance attributes
    _store        : OwnerStore
    _header_names : list[str]

    def __init__(
        self   : Self,
        store  : OwnerStore,
        parent : QWidget | None = None
    ) -> None:
        self._store = store
        model = TableModel()
        model.setHorizontalHeaderGroupLabels(self._headerPairs())
        super().__init__(model, parent)

    def showEvent(self, a0: QShowEvent | None) -> None:
        """Rebuild model from store when widget is shown."""
        super().showEvent(a0)
        self._rebuildModel()

    def _headerPairs(self : Self) -> list[tuple[str, str]]:
        self._header_names = [
            name
            for names in _COLUMNS.values()
            for name in names
        ]
        return [
            (group, "" if "Expander" in name else name)
            for group, names in _COLUMNS.items()
            for name in names
        ]

    def _rebuildModel(self : Self) -> None:
        model = self.model()
        if not isinstance(model, TableModel):
            raise ValueError("Bad model")
        # capture expander states
        property_expanders : dict[PropertiesMixin, bool] = {}
        property_text_expanders : dict[object, bool] = {}
        if (row_count := model.rowCount()) > 0:
            p_exp_idx = self._header_names.index("Property Expander")
            pt_exp_idx = self._header_names.index("Property Text Expander")
            name_idx = self._header_names.index("Name")
            for row_idx in range(row_count):
                p_exp_item = model.item(row_idx, p_exp_idx)
                if isinstance(p_exp_item, PropertiesExpanderItem) \
                and isinstance(p_exp := p_exp_item.value(), bool):
                    owner_id_idx = self._header_names.index("Owner ID")
                    owner_id_item = model.item(row_idx, owner_id_idx)
                    if not isinstance(owner_id_item, PropertiesItem):
                        raise ValueError("Unexpected owner ID item")
                    owner = owner_id_item.ref()
                    if not isinstance(owner, PropertiesMixin):
                        raise ValueError("Unexpected owner type")
                    property_expanders[owner] = p_exp
                pt_exp_item = model.item(row_idx, pt_exp_idx)
                if isinstance(pt_exp_item, PropertiesExpanderItem) \
                and isinstance(pt_exp := pt_exp_item.value(), bool):
                    name_item = model.item(row_idx, name_idx)
                    if not isinstance(name_item, PropertiesItem):
                        raise ValueError("Unexpected property name item")
                    if (state := name_item.ref()) is None:
                        raise ValueError("Unexpected property name ref")
                    property_text_expanders[state] = pt_exp
            model.removeRows(0, row_count)
        # sort items
        pass  # TODO: sort items
        # add new rows
        owner_col_stop = len(_COLUMNS["Owner"])
        property_col = owner_col_stop
        property_col_stop = property_col + len(_COLUMNS["Property"])
        for owner, store_properties in self._store.items():
            owner_row_idx = model.rowCount()
            p_exp = property_expanders.get(owner, True) \
                if len(store_properties) > 1 else None
            if len(store_properties) == 0:
                row = self._emptyRow()
                self._populateOwner(row, owner)
                model.appendRow(row.cells())
                continue
            for property_idx, store_property in enumerate(store_properties):
                property_row_idx = model.rowCount()
                texts = store_property.texts
                pt_exp = \
                    property_text_expanders.get(store_property.current, True) \
                    if len(texts) > 1 else None
                for text_idx in range(max(1, len(texts))):
                    row = self._emptyRow()
                    if property_idx == 0 and text_idx == 0:
                        self._populateOwner(row, owner)
                        if p_exp is not None:
                            row["Property Expander"] = \
                                PropertiesExpanderItem(p_exp)
                    if text_idx == 0:
                        self._populateProperty(row, store_property)
                        if pt_exp is not None:
                            row["Property Text Expander"] = \
                                PropertiesExpanderItem(pt_exp)
                    if text_idx < len(texts):
                        self._populatePropertyText(row, texts[text_idx])
                    model.appendRow(row.cells())
                row_span = model.rowCount() - property_row_idx
                if row_span > 1:
                    for col_idx in range(property_col, property_col_stop):
                        self.setSpan(property_row_idx, col_idx, row_span, 1)
                    if pt_exp is False:
                        for row_idx in range(
                            property_row_idx + 1, model.rowCount()
                        ):
                            self.setRowHidden(row_idx, True)
            row_span = model.rowCount() - owner_row_idx
            if row_span > 1:
                for col_idx in range(owner_col_stop):
                    self.setSpan(owner_row_idx, col_idx, row_span, 1)
                if p_exp is False:
                    for row_idx in range(owner_row_idx + 1, model.rowCount()):
                        self.setRowHidden(row_idx, True)

    def _emptyRow(self : Self) -> TableRow:
        return TableRow(self._header_names)

    def _populateOwner(
        self  : Self,
        row   : TableRow,
        owner : PropertiesMixin
    ) -> TableRow:
        if not isinstance(owner, ItemMixin):
            raise ValueError("Unexpected owner type")
        row["Owner ID"] = PropertiesItem(owner.suid(), owner)
        return row

    def _populateProperty(
        self  : Self,
        row   : TableRow,
        store : StoreProperty,
        new   : bool = False
    ) -> None:
        if store.initial is None:
            raise ValueError("Store property initial is None")
        if store.obj is None:
            raise ValueError("Store property source is None")
        name     = store.current.name
        kind     = store.current.kind
        value    = store.current.value
        custom   = store.obj.isCustom()
        editable = store.obj.writeable()
        p = PropertiesItem
        v = PropertiesValueItem
        row[ "Name"   ] = p(name, store.current, "name", new, not custom)
        row[ "Custom" ] = p(custom, None, None, new, False)
        row[ "Type"   ] = p(kind, store.current, "kind", new, not custom)
        row[ "Value"  ] = v(kind, value, store.current, "value", new, editable)

    def _populatePropertyText(
        self  : Self,
        row   : TableRow,
        store : StorePropertyText,
        new   : bool = False
    ) -> None:
        if store.initial is None:
            raise ValueError("Store property text initial is None")
        p = PropertiesItem
        c = store.current
        row[ "Visible"    ] = p( c.visible    , c , "visible"    , new )
        row[ "Cleat"      ] = p( c.cleat      , c , "cleat"      , new )
        row[ "X"          ] = p( c.x          , c , "x"          , new )
        row[ "Y"          ] = p( c.y          , c , "y"          , new )
        row[ "Rotation"   ] = p( c.rotation   , c , "rotation"   , new )
        row[ "Mirror H"   ] = p( c.mirror_h   , c , "mirror_h"   , new )
        row[ "Mirror V"   ] = p( c.mirror_v   , c , "mirror_v"   , new )
        row[ "Autoflip"   ] = p( c.autoflip   , c , "autoflip"   , new )
        row[ "Origin"     ] = p( c.origin     , c , "origin"     , new )
        row[ "Align H"    ] = p( c.align_h    , c , "align_h"    , new )
        row[ "Align V"    ] = p( c.align_v    , c , "align_v"    , new )
        row[ "Width"      ] = p( c.width      , c , "width"      , new )
        row[ "Height"     ] = p( c.height     , c , "height"     , new )
        row[ "Pad Left"   ] = p( c.pad_left   , c , "pad_left"   , new )
        row[ "Pad Right"  ] = p( c.pad_right  , c , "pad_right"  , new )
        row[ "Pad Top"    ] = p( c.pad_top    , c , "pad_top"    , new )
        row[ "Pad Bottom" ] = p( c.pad_bottom , c , "pad_bottom" , new )
        row[ "Color"      ] = p( c.color      , c , "color"      , new )
        row[ "Font"       ] = p( c.font       , c , "font"       , new )
        row[ "Size"       ] = p( c.size       , c , "size"       , new )
        row[ "Bold"       ] = p( c.bold       , c , "bold"       , new )
        row[ "Italic"     ] = p( c.italic     , c , "italic"     , new )
        row[ "Underline"  ] = p( c.underline  , c , "underline"  , new )
