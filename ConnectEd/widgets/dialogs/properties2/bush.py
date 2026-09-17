from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QTableView, QCheckBox, \
                            QGraphicsItem

from ...graphics.properties import Property, PropertiesMixin

from ...graphics.items.property_text import PropertyTextItem

from ...graphics.items.mixin import ItemMixin

from ..components.table import TableItem, TableModel


ITEM_COLUMNS = [  # level 1 - item
        "Item ID"
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

_HEADER_LABEL_GROUPS = [
    ITEM_COLUMNS,
    PROPERTY_COLUMNS,
    PROPERTY_TEXT_COLUMNS,
]


TableRow = list[TableItem | None]


class PropertiesBushWidget(QTableView):
    """
    Compressed tree widget.
    Level 1 rows = items
    Level 2 rows = properties
    Level 3 rows = property texts (may be hidden)
    Cells of the first child row are promoted to sit alongside parent cells.
    This works because each level has its own set of columns.
    Cell merge and branch indicators give tree appearance/behaviour.
    """

    # instance attributes
    _header_labels : list[str]

    def __init__(
        self               : Self,
        items              : list[PropertiesMixin],
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # create model
        model = TableModel()
        # get property names
        property_names = set()
        for item in items:
            for property_name in item.properties.keys():
                property_names.add(property_name)
        # create header labels
        self._header_labels = []
        for header_label_group in _HEADER_LABEL_GROUPS:
            for header_label in header_label_group:
                if "Expander" in header_label:
                    header_label = ""
                self._header_labels.append(header_label)
        model.setHorizontalHeaderLabels(self._header_labels)
        # build model
        for item in items:
            if not isinstance(item, ItemMixin):
                continue
            item_row_idx = model.rowCount()      # track item rows
            row = self._emptyRow()               # initialize row
            row = self._populateItem(row, item)  # populate item columns
            property_row_idx = item_row_idx      # track property rows
            for property in item.properties.values():
                property_row_idx = model.rowCount()
                # populate property columns
                row = self._populateProperty(row, property)
                if not isinstance(item, QGraphicsItem):
                    continue
                property_texts = [
                    child for child in item.childItems()
                    if isinstance(child, PropertyTextItem)
                ]
                for i, child in enumerate(property_texts):
                    row_copy = row.copy()
                    # populate property text columns
                    row = self._populatePropertyText(row, child, i)
                    # add row to model if applicable
                    if i == len(property_texts) - 1:
                        model.appendRow(row)
                        row = row_copy
                # add last (or only) property row to model
                model.appendRow(row)
                # merge property cells to span property texts, if applicable
                row_span = model.rowCount() - property_row_idx
                if row_span > 1:
                    col_start = len(ITEM_COLUMNS)
                    col_stop = col_start + len(PROPERTY_COLUMNS)
                    for col_idx in range(col_start, col_stop):
                        self.setSpan(property_row_idx, col_idx, row_span, 1)
            # merge item cells to span properties, if applicable
            row_span = model.rowCount() - item_row_idx
            if row_span > 1:
                for col_idx in range(len(ITEM_COLUMNS)):
                    self.setSpan(item_row_idx, col_idx, row_span, 1)

    def _emptyRow(self : Self) -> TableRow:
        return [None] * len(self._header_labels)

    def _populateItem(
        self : Self,
        row  : TableRow,
        item : ItemMixin
    ) -> TableRow:
        row[self._header_labels.index("Item ID")] = \
            TableItem(item.suid())
        return row

    def _populateProperty(
        self     : Self,
        row      : TableRow,
        property : Property
    ) -> TableRow:
        fields = {}
        fields[ "Name"   ] = property.name()
        fields[ "Custom" ] = property.isCustom()
        fields[ "Type"   ] = property.kind()
        fields[ "Value"  ]   = property.value()
        for key, value in fields.items():
            row[self._header_labels.index(key)] = TableItem(value)
        return row

    def _populatePropertyText(
        self          : Self,
        row           : TableRow,
        property_text : PropertyTextItem
    ) -> TableRow:
        fields = {}
        fields[ "Visible"    ] = property_text.isVisible()
        fields[ "Cleat"      ] = property_text.cleat()
        fields[ "X"          ] = property_text.x()
        fields[ "Y"          ] = property_text.y()
        fields[ "Rotation"   ] = property_text.rotation()
        fields[ "Mirror H"   ] = property_text.mirrorH()
        fields[ "Mirror V"   ] = property_text.mirrorV()
        fields[ "Autoflip"   ] = property_text.autoflip()
        fields[ "Origin"     ] = property_text.origin()
        fields[ "Align H"    ] = property_text.alignH()
        fields[ "Align V"    ] = property_text.alignV()
        fields[ "Width"      ] = property_text.width()
        fields[ "Height"     ] = property_text.height()
        fields[ "Pad Left"   ] = property_text.padLeft()
        fields[ "Pad Right"  ] = property_text.padRight()
        fields[ "Pad Top"    ] = property_text.padTop()
        fields[ "Pad Bottom" ] = property_text.padBottom()
        fields[ "Color"      ] = property_text.color()
        fields[ "Font"       ] = property_text.font()
        fields[ "Size"       ] = property_text.textSize()
        fields[ "Bold"       ] = property_text.textBold()
        fields[ "Italic"     ] = property_text.textItalic()
        fields[ "Underline"  ] = property_text.textUnderline()
        for key, value in fields.items():
            row[self._header_labels.index(key)] = TableItem(value)
        return row

