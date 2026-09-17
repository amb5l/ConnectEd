from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QTableView, QCheckBox, \
                            QGraphicsItem

from ...graphics.properties import Property, PropertiesMixin

from ...graphics.items.property_text import PropertyTextItem

from ...graphics.items.mixin import ItemMixin

from ..components.table import TableItem, TableModel


OWNER_COLUMNS = [  # level 1 - owner
        "Owner ID"
    ]

PROPERTY_COLUMNS = [  # level 2 - property
        "Property Expander",
        "Name",
        "Custom",
        "Type",
        "Value"
    ]

PROPERTY_TEXT_COLUMNS = [  # level 3 - property text
        "Property Text Expander",
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
    ]

_COLUMN_GROUPS = [
    OWNER_COLUMNS,
    PROPERTY_COLUMNS,
    PROPERTY_TEXT_COLUMNS,
]


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


class PropertiesBushWidget(QTableView):
    """
    Compressed tree widget.
    Level 1 rows = owners
    Level 2 rows = properties
    Level 3 rows = property texts
    Cells of the first child row are promoted to sit alongside parent cells.
    This works because each level has its own set of columns.
    Cell merge, and expanders, give tree-like appearance/behaviour.
    """

    # instance attributes
    _header_names  : list[str]
    _model         : TableModel

    def __init__(
        self               : Self,
        owners             : list[PropertiesMixin],
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        model = TableModel()
        model.setHorizontalHeaderLabels(self._getHeaderLabels())
        self._buildModel(model, owners)

    def _getHeaderLabels(self : Self) -> list[str]:
        self._header_names = []
        header_labels = []
        for column_group in _COLUMN_GROUPS:
            for header_name in column_group:
                self._header_names.append(header_name)
                header_label = "" if "Expander" in header_name else header_name
                header_labels.append(header_label)
        return header_labels

    def _buildModel(
        self   : Self,
        model  : TableModel,
        owners : list[PropertiesMixin]
    ) -> None:
        # capture expander states
        property_expanders      : dict[PropertiesMixin, bool] = {}
        property_text_expanders : dict[Property, bool] = {}
        if row_count := model.rowCount() > 1:
            p_exp_idx = self._header_names.index("Property Expander")
            pt_exp_idx = self._header_names.index("Property Text Expander")
            for row_idx in range(model.rowCount()):
                p_exp_item = model.item(row_idx, p_exp_idx)
                if isinstance(p_exp_item, TableItem) \
                and isinstance(p_exp := p_exp_item.value(), bool):
                    owner_id_idx = self._header_names.index("Owner ID")
                    owner_id_item = model.item(row_idx, owner_id_idx)
                    if not isinstance(owner_id_item, TableItem):
                        raise ValueError("Unexpected owner ID item")
                    owner = owner_id_item.ref()
                    if not isinstance(owner, PropertiesMixin):
                        raise ValueError("Unexpected owner type")
                    property_expanders[owner] = p_exp
                pt_exp_item = model.item(row_idx, pt_exp_idx)
                if isinstance(pt_exp_item, TableItem) \
                and isinstance(pt_exp := pt_exp_item.value(), bool):
                    property_name_idx = self._header_names.index("Property")
                    property_name_item = model.item(row_idx, property_name_idx)
                    if not isinstance(property_name_item, TableItem):
                        raise ValueError("Unexpected property name item")
                    property = property_name_item.ref()
                    if not isinstance(property, Property):
                        raise ValueError("Unexpected property name type")
                    property_text_expanders[property] = pt_exp
        # clear existing rows
        if row_count > 0:
            model.removeRows(0, model.rowCount())
        # sort items
        pass  # TODO: sort items
        # add new rows
        for owner in owners:
            if not isinstance(owner, ItemMixin):
                continue
            owner_row_idx = model.rowCount()      # track item rows
            row = self._emptyRow()               # initialize row
            row = self._populateOwner(row, owner)  # populate owner columns
            property_row_idx = owner_row_idx      # track property rows
            # property expander
            p_exp = None
            if len(owner.properties) > 1:
                p_exp = property_expanders.get(owner, True)
                row["Property Expander"] = TableItem(p_exp)
            # property rows
            for property in owner.properties.values():
                property_row_idx = model.rowCount()
                # populate property columns
                row = self._populateProperty(row, property)
                if not isinstance(owner, QGraphicsItem):
                    continue
                # get property texts
                property_texts = [
                    child for child in owner.childItems()
                    if isinstance(child, PropertyTextItem)
                ]
                # property text expander
                pt_exp = None
                if len(property_texts) > 1:
                    pt_exp = property_text_expanders.get(property, True)
                    row["Property Text Expander"] = TableItem(pt_exp)
                # property text rows
                for i, child in enumerate(property_texts):
                    row_copy = row.copy()
                    # populate property text columns
                    row = self._populatePropertyText(row, child)
                    # add row to model if applicable
                    if i == len(property_texts) - 1:
                        model.appendRow(row)
                        row = row_copy
                # add last (or only) property row to model
                model.appendRow(row)
                # get property text row span for this property
                row_span = model.rowCount() - property_row_idx
                if row_span > 1:
                    # merge property cells to span property texts
                    col_start = len(OWNER_COLUMNS)
                    col_stop = col_start + len(PROPERTY_COLUMNS)
                    for col_idx in range(col_start, col_stop):
                        self.setSpan(property_row_idx, col_idx, row_span, 1)
                    # hide 2nd children if expander is closed
                    if pt_exp is False:
                        for row_idx in range(property_row_idx + 1, model.rowCount()):
                            self.setRowHidden(row_idx, True)
            # get property row span for this owner
            row_span = model.rowCount() - owner_row_idx
            if row_span > 1:
                # merge owner cells to span property rows
                for col_idx in range(len(OWNER_COLUMNS)):
                    self.setSpan(owner_row_idx, col_idx, row_span, 1)
                # hide 2nd children if expander is closed
                if p_exp is False:
                    pass  # TODO: hide 2nd children if expander is closed
                    for row_idx in range(owner_row_idx + 1, model.rowCount()):
                        self.setRowHidden(row_idx, True)
        self.setModel(model)

    def _emptyRow(self : Self) -> TableRow:
        return TableRow(self._header_names)

    def _populateOwner(
        self  : Self,
        row   : TableRow,
        owner : ItemMixin
    ) -> TableRow:
        row["Owner ID"] = TableItem(owner.suid(), owner)
        return row

    def _populateProperty(
        self     : Self,
        row      : TableRow,
        property : Property
    ) -> TableRow:
        row[ "Name"   ] = TableItem(property.name(), property)
        row[ "Custom" ] = TableItem(property.isCustom())
        row[ "Type"   ] = TableItem(property.kind())
        row[ "Value"  ] = TableItem(property.value())
        return row

    def _populatePropertyText(
        self : Self,
        row  : TableRow,
        pt   : PropertyTextItem
    ) -> TableRow:
        row[ "Visible"    ] = TableItem(pt.isVisible(), pt)
        row[ "Cleat"      ] = TableItem(pt.cleat())
        row[ "X"          ] = TableItem(pt.x())
        row[ "Y"          ] = TableItem(pt.y())
        row[ "Rotation"   ] = TableItem(pt.rotation())
        row[ "Mirror H"   ] = TableItem(pt.mirrorH())
        row[ "Mirror V"   ] = TableItem(pt.mirrorV())
        row[ "Autoflip"   ] = TableItem(pt.autoflip())
        row[ "Origin"     ] = TableItem(pt.origin())
        row[ "Align H"    ] = TableItem(pt.alignH())
        row[ "Align V"    ] = TableItem(pt.alignV())
        row[ "Width"      ] = TableItem(pt.width())
        row[ "Height"     ] = TableItem(pt.height())
        row[ "Pad Left"   ] = TableItem(pt.padLeft())
        row[ "Pad Right"  ] = TableItem(pt.padRight())
        row[ "Pad Top"    ] = TableItem(pt.padTop())
        row[ "Pad Bottom" ] = TableItem(pt.padBottom())
        row[ "Color"      ] = TableItem(pt.color())
        row[ "Font"       ] = TableItem(pt.font())
        row[ "Size"       ] = TableItem(pt.textSize())
        row[ "Bold"       ] = TableItem(pt.textBold())
        row[ "Italic"     ] = TableItem(pt.textItalic())
        row[ "Underline"  ] = TableItem(pt.textUnderline())
        return row
