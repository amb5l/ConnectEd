from __future__ import annotations

from typing      import Self, Callable, Any
from dataclasses import dataclass

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QCheckBox, QAbstractItemView
from PyQt6.QtGui     import QShowEvent, QStandardItem

from ....app import logger

from ....core.check import checked
from ....core.types import DataKind

from ...graphics.properties import Property, PropertiesMixin, PropertyDisplayState

from ...graphics.items.property_text import PropertyTextItem

from ...graphics.items.mixin import ItemMixin

from ...graphics.items.mixin.handle import ItemHandlesMixin

from ..components.table import TableItem, TableModel, TableProxy, TableView

from .item     import PropertiesItem
from .delegate import PropertiesDelegate

@dataclass
class FieldSpec:
    label  : str


@dataclass
class ItemFieldSpec(FieldSpec):
    getter : Callable[[ItemMixin], Any]

    def editable(self : Self) -> bool:
        return False


@dataclass
class PropertyFieldSpec(FieldSpec):
    kind   : DataKind
    getter : Callable[[Property], Any]

    def editable(self : Self, custom : bool) -> bool:
        return self.label != "Custom" and \
            ((self.label != "Name" and self.label != "Kind") or custom)

@dataclass
class DisplayFieldSpec(FieldSpec):
    kind   : DataKind
    getter : Callable[[PropertyTextItem], Any]

    def editable(self : Self) -> bool:
        return True


_FIELD_SPECS = [

    ItemFieldSpec     ( "Item ID"   , ItemMixin.suid ),

    PropertyFieldSpec ( "Name"    , DataKind.STR   , Property.name     ),
    PropertyFieldSpec ( "Custom"  , DataKind.BOOL  , Property.isCustom ),
    PropertyFieldSpec ( "Kind"    , DataKind.KIND  , Property.kind     ),
    PropertyFieldSpec ( "Value"   , DataKind.DUMMY , Property.value    ),
    PropertyFieldSpec ( "Display" , DataKind.BOOL  , Property.display  ),

    DisplayFieldSpec  ( "Visible"    , DataKind.BOOL        , PropertyTextItem.isVisible     ),
    DisplayFieldSpec  ( "Cleat"      , DataKind.DUMMY       , PropertyTextItem.cleat         ),
    DisplayFieldSpec  ( "X"          , DataKind.FLOAT       , PropertyTextItem.x             ),
    DisplayFieldSpec  ( "Y"          , DataKind.FLOAT       , PropertyTextItem.y             ),
    DisplayFieldSpec  ( "Rotation"   , DataKind.FLOAT       , PropertyTextItem.rotation      ),
    DisplayFieldSpec  ( "Mirror H"   , DataKind.BOOL        , PropertyTextItem.mirrorH       ),
    DisplayFieldSpec  ( "Mirror V"   , DataKind.BOOL        , PropertyTextItem.mirrorV       ),
    DisplayFieldSpec  ( "Autoflip"   , DataKind.BOOL        , PropertyTextItem.autoflip      ),
    DisplayFieldSpec  ( "Origin"     , DataKind.RECT_HANDLE , PropertyTextItem.origin        ),
    DisplayFieldSpec  ( "Align H"    , DataKind.ALIGN_H     , PropertyTextItem.alignH        ),
    DisplayFieldSpec  ( "Align V"    , DataKind.ALIGN_V     , PropertyTextItem.alignV        ),
    DisplayFieldSpec  ( "Width"      , DataKind.FLOAT       , PropertyTextItem.width         ),
    DisplayFieldSpec  ( "Height"     , DataKind.FLOAT       , PropertyTextItem.height        ),
    DisplayFieldSpec  ( "Pad Left"   , DataKind.FLOAT       , PropertyTextItem.padLeft       ),
    DisplayFieldSpec  ( "Pad Right"  , DataKind.FLOAT       , PropertyTextItem.padRight      ),
    DisplayFieldSpec  ( "Pad Top"    , DataKind.FLOAT       , PropertyTextItem.padTop        ),
    DisplayFieldSpec  ( "Pad Bottom" , DataKind.FLOAT       , PropertyTextItem.padBottom     ),
    DisplayFieldSpec  ( "Color"      , DataKind.COLOR       , PropertyTextItem.textColor     ),
    DisplayFieldSpec  ( "Font"       , DataKind.FONT_FAMILY , PropertyTextItem.textFont      ),
    DisplayFieldSpec  ( "Size"       , DataKind.FONT_SIZE   , PropertyTextItem.textSize      ),
    DisplayFieldSpec  ( "Bold"       , DataKind.BOOL        , PropertyTextItem.textBold      ),
    DisplayFieldSpec  ( "Italic"     , DataKind.BOOL        , PropertyTextItem.textItalic    ),
    DisplayFieldSpec  ( "Underline"  , DataKind.BOOL        , PropertyTextItem.textUnderline )

]


class PropertiesListWidget(TableView):
    """
    Widget for displaying properties in a list.
    """

    _transpose_checkbox : QCheckBox
    _model              : TableModel
    _proxy              : TableProxy
    _delegates          : list[PropertiesDelegate]

    def __init__(
        self               : Self,
        items              : list[PropertiesMixin],
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        # build model
        self._model = TableModel()
        # header labels
        header_labels = []
        for spec in _FIELD_SPECS:
            header_labels.append(spec.label)
        self._model.setHorizontalHeaderLabels(header_labels)
        # create and assign delegates (must keep references to prevent GC)
        self._delegates = []
        for col_idx, header_label in enumerate(header_labels):
            if header_label == "Item ID":
                continue
            delegate = PropertiesDelegate(self)
            self._delegates.append(delegate)
            self.setItemDelegateForColumn(col_idx, delegate)
        # all items
        for item in items:
            if not isinstance(item, ItemMixin):
                raise ValueError(f"Item {item} is not a ItemMixin")
            # create property rows per item
            for property_name in item.properties.keys():
                property = item.properties[property_name]
                display_item = property.displayItem()
                row = []
                # create cells per row
                for spec in _FIELD_SPECS:
                    label = spec.label
                    getter = spec.getter
                    if isinstance(spec, ItemFieldSpec):
                        value = getter(item)
                        editable = spec.editable()
                        table_item = TableItem(
                            value, ref=item, editable=editable
                        )
                    elif isinstance(spec, PropertyFieldSpec):
                        kind = spec.kind
                        if kind == DataKind.DUMMY:
                            if label == "Value":
                                kind = property.kind()
                            else:
                                raise ValueError(f"Invalid label: {label}")
                        value = getter(property)
                        editable = spec.editable(property.isCustom())
                        table_item = PropertiesItem(
                            kind     = kind,
                            value    = value,
                            editable = editable
                        )
                    elif isinstance(spec, DisplayFieldSpec):
                        if display_item is None:
                            table_item = None
                        else:
                            kind = spec.kind
                            if kind == DataKind.DUMMY:
                                if label == "Cleat":
                                    if not isinstance(item, ItemHandlesMixin):
                                        raise ValueError(f"Item {item} is not a ItemHandlesMixin")
                                    kind  = item.handleIdKind()
                                    value = next(iter(item.handles()))
                                else:
                                    raise ValueError(f"Invalid label: {label}")
                            value = getter(display_item)
                            editable = spec.editable()
                            table_item = PropertiesItem(
                                kind     = kind,
                                value    = value,
                                editable = editable
                            )
                    else:
                        raise ValueError(f"Invalid group: {spec.group}")
                    row.append(table_item)
                self._model.appendRow(row)
        # set edit triggers
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )

        # superclass init
        super().__init__(self._model, parent)
        # create transpose proxy
        self._proxy = TableProxy(self._model)
        # set model
        self.setModel(self._model)
        # transpose checkbox
        transpose_checkbox.stateChanged.connect(
            self._onTransposeCheckboxChanged
        )
        self._transpose_checkbox = transpose_checkbox
        # item changes
        self._model.itemChanged.connect(self._onItemChanged)

    def showEvent(self : Self, a0 : QShowEvent | None) -> None:
        if a0 is not None:
            transposed = self.model() is self._proxy
            self._transpose_checkbox.setChecked(transposed)
        super().showEvent(a0)

    def _onTransposeCheckboxChanged(self : Self, state : Qt.CheckState) -> None:
        self.setModel(
            self._proxy if state == Qt.CheckState.Checked else self._model
        )

    @checked
    def _onItemChanged(self : Self, item : QStandardItem) -> None:
        if not isinstance(item, PropertiesItem):
            return
        col = item.column()
        if not (0 <= col < len(_FIELD_SPECS)):
            return
        spec = _FIELD_SPECS[col]
        if spec.label != "Display":
            return
        self._updateDisplayFields(item.row(), item.value() is True)

    @checked
    def _updateDisplayFields(self : Self, row : int, enable : bool) -> None:
        owner_item = self._model.item(row, 0)
        owner = owner_item.ref() if isinstance(owner_item, TableItem) \
            else None
        self._model.blockSignals(True)
        try:
            for col, spec in enumerate(_FIELD_SPECS):
                if not isinstance(spec, DisplayFieldSpec):
                    continue
                cell = self._model.item(row, col)
                if enable:
                    if cell is None:
                        self._model.setItem(
                            row, col, self._makeDisplayCell(spec, owner)
                        )
                        continue
                    if not isinstance(cell, TableItem):
                        logger().error(
                            f"Display cell at ({row}, {col}) is not a TableItem"
                        )
                        continue
                    cell.setDeleted(False)
                    cell.setEditable(True)
                else:
                    if cell is None:
                        continue
                    if not isinstance(cell, TableItem):
                        logger().error(
                            f"Display cell at ({row}, {col}) is not a TableItem"
                        )
                        continue
                    if cell.new():
                        self._model.takeItem(row, col)
                    else:
                        cell.setDeleted(True)
                        cell.setEditable(False)
        finally:
            self._model.blockSignals(False)

    @checked
    def _makeDisplayCell(
        self  : Self,
        spec  : DisplayFieldSpec,
        owner : object
    ) -> PropertiesItem:
        kind  = spec.kind
        # get default value
        attr  = spec.label.lower().replace(" ", "_")
        value = getattr(PropertyDisplayState(), attr)
        if kind == DataKind.DUMMY:
            if spec.label != "Cleat":
                raise ValueError(f"Invalid label: {spec.label}")
            if not isinstance(owner, ItemHandlesMixin):
                raise ValueError(f"Item {owner} is not a ItemHandlesMixin")
            kind  = owner.handleIdKind()
            value = next(iter(owner.handles()))
        # create item
        return PropertiesItem(
            kind     = kind,
            value    = value,
            new      = True,
            editable = True
        )