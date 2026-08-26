from __future__ import annotations

from typing import Self, Any
from enum   import StrEnum

from PyQt6.QtCore    import Qt, QModelIndex, QItemSelectionModel, QItemSelection
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QMessageBox, QPushButton, QAbstractItemView
from PyQt6.QtGui     import QColor, QFontDatabase

from ....app import logger

from ....core.check import checked
from ....core.types import (
    NoChange, NO_CHANGE, AlignH, AlignV, HandleId, DataKind,
    RectHandleId, LineHandleId, BlockPinHandleId, SymbolPinHandleId
)
from ....core.utils import removeSuffixes

from ...graphics.properties import PropertiesMixin

from ...graphics.items.mixin.handle import ItemHandlesMixin

from ..components.table import TableModel, TreeTableView

from .item import ChangeItem, \
                  ExistingPropertyChangeItem, NewPropertyChangeItem, \
                  ExistingPropertyTextChangeItem, NewPropertyTextChangeItem, \
                  PropertiesItem

from .delegate import PropertiesDelegate

from .types import (
    ExistingChange, NewChange,
    PropertyChangeAdd, PropertyChangeModify, PropertyChangeDelete,
    PropertyTextChangeAdd, PropertyTextChangeModify, PropertyTextChangeDelete,
    PropertyChangeType
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.views.diagram import DiagramView
    from ...graphics.items.property_text import PropertyTextItem


_PROP_COLS : list[str] = ["Name", "Custom", "Type", "Value"]

_PT_COLS = {
#                   kind                   initial value              method
    "Visible"   : ( DataKind.BOOL        , True                     , PropertyTextItem.isVisible     ),  # noqa E501
    "Cleat"     : ( None                 , None                     , PropertyTextItem.cleat         ),  # noqa E501
    "X"         : ( DataKind.FLOAT       , 0.0                      , PropertyTextItem.x             ),  # noqa E501
    "Y"         : ( DataKind.FLOAT       , 0.0                      , PropertyTextItem.y             ),  # noqa E501
    "Rotation"  : ( DataKind.ROTATION    , 0.0                      , PropertyTextItem.rotation      ),  # noqa E501
    "Mirror H"  : ( DataKind.BOOL        , False                    , PropertyTextItem.mirrorH       ),  # noqa E501
    "Mirror V"  : ( DataKind.BOOL        , False                    , PropertyTextItem.mirrorV       ),  # noqa E501
    "Auto Flip" : ( DataKind.BOOL        , True                     , PropertyTextItem.autoflip      ),  # noqa E501
    "Origin"    : ( DataKind.RECT_HANDLE , RectHandleId.BOTTOM_LEFT , PropertyTextItem.origin        ),  # noqa E501
    "Align H"   : ( DataKind.ALIGN_H     , AlignH.LEFT              , PropertyTextItem.alignH        ),  # noqa E501
    "Align V"   : ( DataKind.ALIGN_V     , AlignV.TOP               , PropertyTextItem.alignV        ),  # noqa E501
    "Height"    : ( DataKind.SIZE        , None                     , PropertyTextItem.height        ),  # noqa E501
    "Width"     : ( DataKind.SIZE        , None                     , PropertyTextItem.width         ),  # noqa E501
    "Color"     : ( DataKind.COLOR       , None                     , PropertyTextItem.textColor     ),  # noqa E501
    "Font"      : ( DataKind.FONT_FAMILY , None                     , PropertyTextItem.textFont      ),  # noqa E501
    "Size"      : ( DataKind.FONT_SIZE   , None                     , PropertyTextItem.textSize      ),  # noqa E501
    "Bold"      : ( DataKind.FONT_BOOL   , None                     , PropertyTextItem.textBold      ),  # noqa E501
    "Italic"    : ( DataKind.FONT_BOOL   , None                     , PropertyTextItem.textItalic    ),  # noqa E501
    "Underline" : ( DataKind.FONT_BOOL   , None                     , PropertyTextItem.textUnderline )   # noqa E501
}

_COLS : list[str] = _PROP_COLS + list(_PT_COLS.keys())

_HEADINGS = \
    [("Property", "Change")] + \
    [("Property", name) for name in _PROP_COLS] + \
    [("Text(s)", "Change")] + \
    [("Text(s)", name) for name in _PT_COLS]

_HANDLE_KIND : dict[type, DataKind] = {
    RectHandleId      : DataKind.RECT_HANDLE,
    LineHandleId      : DataKind.LINE_HANDLE,
    BlockPinHandleId  : DataKind.BLOCK_PIN_HANDLE,
    SymbolPinHandleId : DataKind.SYMBOL_PIN_HANDLE
}


class ExistingPropertyChange(StrEnum):
    NO_CHANGE = "No Change"
    MODIFY    = "Modify"
    DELETE    = "Delete"


NewPropertyChange = "Add"


class PropertiesDialog(QDialog):
    _obj             : PropertiesMixin
    _property_texts  : dict[str, list[PropertyTextItem]]
    _dialog_layout   : QVBoxLayout
    _table_model     : TableModel
    _table_view      : TreeTableView
    _button_layout   : QHBoxLayout
    _display_button  : QPushButton
    _add_prop_button : QPushButton
    _del_prop_button : QPushButton
    _add_text_button : QPushButton
    _del_text_button : QPushButton
    _ok_button       : QPushButton
    _cancel_button   : QPushButton
    _delegates       : list[PropertiesDelegate]
    _selected_index  : QModelIndex | None

    @checked
    def __init__(
        self : Self,
        obj  : PropertiesMixin,
        view : DiagramView | None = None
    ) -> None:
        # superclass init
        super().__init__(view)
        # object, name, texts
        self._obj = obj
        self._property_texts = obj.propertyTexts()
        obj_name = removeSuffixes(obj.__class__.__name__, "Item", "Scene")
        # basic dialog setup
        self.setWindowTitle(f"{obj_name} Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # create model
        self._table_model = TableModel()
        # set headers
        self._table_model.setHorizontalHeaderGroupLabels(_HEADINGS)
        # add rows
        row_idx = 0
        for name in obj.properties.keys():
            if (kind := obj.propertyKind(name)) is None:
                logger().error(f"No kind for property {name}")
                continue
            property = obj.properties[name]
            value = property.value()
            custom = property.isCustom()
            if name not in self._property_texts \
            or len(property_texts := self._property_texts[name]) == 0:
                row = self._buildPropertyRow(name, custom, kind, value)
            elif len(property_texts) == 1:
                # single property text -> inline with property
                pt = property_texts[0]
                row = self._buildPropertyRow(name, custom, kind, value, pt)
            else:
                # multiple property texts -> child rows
                row = self._buildPropertyRow(name, custom, kind, value)
                self._table_model.appendRow(row)
                parent = row[0]
                if parent is None:
                    raise ValueError("Bad parent item")
                for pt in property_texts:
                    row = self._buildPropertyTextRow(pt)
                    parent.appendRow(row)
            self._table_model.appendRow(row)
            row_idx += 1
        # create table view
        self._table_view = TreeTableView(self._table_model)
        # selection mode and behaviour
        self._table_view.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._table_view.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectItems
        )
        # hook selection changes
        selection_model = self._table_view.selectionModel()
        if selection_model is None:
            raise ValueError("Bad selection model")
        self._selected_index = None
        selection_model.selectionChanged.connect(self._onSelectionChanged)
        # create and assign delegates (must keep references to prevent GC)
        self._delegates = []
        for col_idx in range(self._table_model.columnCount()):
            delegate = PropertiesDelegate(self)
            self._delegates.append(delegate)
            self._table_view.setItemDelegateForColumn(col_idx, delegate)
        # set edit triggers
        self._table_view.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        # refresh entire table
        self._refreshTable()
        # resize columns
        self._table_view.resizeColumnsToContents()
        self._table_view.setColumnWidth(
            _COLS.index("Value"), self._getValueColumnWidth()
        )
        # buttons
        self._button_layout = QHBoxLayout()
        self._add_prop_button = QPushButton("Add Property")
        self._add_prop_button.clicked.connect(self._addProperty)
        self._button_layout.addWidget(self._add_prop_button)
        self._del_prop_button = QPushButton("Delete Property")
        self._del_prop_button.setEnabled(False)  # nothing selected initially
        self._del_prop_button.clicked.connect(self._deleteRows)
        self._button_layout.addWidget(self._del_prop_button)
        self._add_text_button = QPushButton("Add Text")
        self._add_text_button.setEnabled(False)  # nothing selected initially
        self._add_text_button.clicked.connect(self._addTextRow)
        self._button_layout.addWidget(self._add_text_button)
        self._del_text_button = QPushButton("Delete Text")
        self._del_text_button.setEnabled(False)  # nothing selected initially
        self._del_text_button.clicked.connect(self._deleteTextRows)
        self._button_layout.addWidget(self._del_text_button)
        self._button_layout.addStretch()
        self._ok_button = QPushButton("OK")
        self._ok_button.clicked.connect(self.accept)
        self._button_layout.addWidget(self._ok_button)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)
        # finalise
        self._dialog_layout.addWidget(self._table_view)
        self._dialog_layout.addLayout(self._button_layout)
        self.setLayout(self._dialog_layout)
        self.adjustSize()
        header = self._table_view.header()
        if header is not None:
            min_width = header.length() + 50
            min_height = header.sizeHint().height() + 50
            self.setMinimumSize(min_width, min_height)
        self._table_model.dataChanged.connect(self._onDataChanged)

    def accept(self : Self) -> None:
        name_col = _COLS.index("Name")
        custom_col = _COLS.index("Custom")
        kind_col = _COLS.index("Type")
        value_col = _COLS.index("Value")
        names : list[str] = []
        for row in range(self._table_model.rowCount()):
            # check for invalid or duplicate names
            if (name_item := self._getItem(row, name_col)) is None:
                logger().error(f"Bad name item for row {row}")
                continue
            if name_item.deleted():
                continue
            if not isinstance(name := name_item.value(), str):
                logger().error(f"Name is not a string: {name}")
                return
            if name == "" or name in names:
                QMessageBox.warning(
                    self, "Invalid Property",
                    "Property names must be non-empty and unique."
                )
                index = self._table_model.index(row, name_col)
                self._table_view.setCurrentIndex(index)
                self._table_view.edit(index)
                return
            names.append(name)
            # check custom, kind, value
            if (custom_item := self._getItem(row, custom_col)) is None:
                logger().error(f"Bad custom item for row {row}")
                continue
            if not isinstance(custom := custom_item.value(), bool):
                logger().error(f"Custom is not a bool: {custom}")
                return
            if (kind_item := self._getItem(row, kind_col)) is None:
                logger().error(f"Bad kind item for row {row}")
                continue
            if not isinstance(kind := kind_item.value(), DataKind):
                logger().error(f"Kind is not a DataKind: {kind}")
                return
            if custom and kind != DataKind.STR and kind != DataKind.TEXT:
                logger().error(f"Custom property '{name}' must have string/text type")
                return
            if (value_item := self._getItem(row, value_col)) is None:
                logger().error(f"Bad value item for row {row}")
                continue
            if kind != value_item.kind():
                logger().warning(f"Type/value mismatch for property '{name}'")
                value_item.setKind(kind)
            if not isinstance(value_item.value(), kind.types()):
                QMessageBox.warning(
                    self, "Invalid Property",
                    f"Value of property '{name}' does not match type '{kind}'."
                )
                index = self._table_model.index(row, value_col)
                self._table_view.setCurrentIndex(index)
                self._table_view.edit(index)
                return
        super().accept()

    @checked
    def getChanges(self : Self) -> list[PropertyChangeType]:
        """
        Returns a list of changes to be applied to the item.
        """
        def _item(i : int, col_name : str) -> PropertiesItem:
            item = self._getItem(i, _COLS.index(col_name))
            if item is None:
                raise ValueError(f"Bad item for row {i} and column {col_name}")
            return item
        def _itemValue(i : int, col_name : str, type_ : type | tuple[type, ...]) -> Any:
            item = _item(i, col_name)
            if not isinstance(value := item.value(), type_):
                raise ValueError(f"Value is not a {type_}: {value}")
            return value
        def _itemAndValue(
            i        : int,
            col_name : str,
            type_    : type | tuple[type, ...]
        ) -> tuple[PropertiesItem, Any]:
            item = self._getItem(i, _COLS.index(col_name))
            if item is None:
                raise ValueError(f"Bad item for row {i} and column {col_name}")
            value = item.value()
            if not isinstance(value, type_):
                raise ValueError(f"Value is not a {type_}: {value}")
            return item, value
        model = self._table_model
        changes : list[PropertyChangeType] = []
        # process all rows
        for row_idx in range(model.rowCount()):
            name_item, name = _itemAndValue(row_idx, "Name", str)
            # determine property text row(s)
            visible_item = self._getItem(row_idx, _COLS.index("Visible"))
            if visible_item is None:
                pt_parent = name_item
                pt_row_range = range(name_item.rowCount())
            else:
                pt_parent = model
                pt_row_range = range(row_idx, row_idx+1)
            # process property text row(s)
            def _getPTItem(
                parent   : TableModel | PropertiesItem,
                row_idx  : int,
                col_name : str
            ) -> PropertiesItem:
                if isinstance(parent, TableModel):
                    item = parent.item(row_idx, _COLS.index(col_name))
                elif isinstance(parent, PropertiesItem):
                    item = parent.child(row_idx, _COLS.index(col_name))
                else:
                    raise ValueError(f"Bad parent: {parent}")
                if not isinstance(item, PropertiesItem):
                    raise ValueError(f"Item is not a PropertiesItem: {item}")
                return item
            for pt_row_idx in pt_row_range:
                visible_item = _getPTItem(pt_parent, pt_row_idx, "Visible")
                if visible_item.deleted():
                    ref = visible_item.ref()
                    if not isinstance(ref, PropertyTextItem):
                        raise ValueError(f"Bad reference: {ref}")
                    changes.append(PropertyTextChangeDelete(ref))
                elif visible_item.new():
                    # addition
                    pt_args = self._getRowPropertyTextItemValues(row_idx)
                    if pt_args is None:
                        raise ValueError(f"Bad PT arguments for row {row_idx}")
                    changes.append(PropertyTextChangeAdd(name, *pt_args))
                else:
                    # any modifications?
                    pass


            else

            if visible_item is None:
                # no inline property text so look at child rows
                for j in range(name_item.rowCount()):
                    visible_item = name_item.child(j, _COLS.index("Visible"))


            if name_item.deleted():
                # deletion
                changes.append(PropertyChangeDelete(name))
                continue
            custom_item, custom = _itemAndValue(row_idx, "Custom", bool)
            kind_item, kind = _itemAndValue(row_idx, "Type", DataKind)
            value_item, value = _itemAndValue(row_idx, "Value", kind.types())
            if name_item.new():
                # addition
                changes.append(PropertyChangeAdd(name, kind, value))
                continue
            # modification
            if name_item.changed() \
            or kind_item.changed() \
            or value_item.changed():
                changes.append(PropertyChangeModify(name, kind, value))
            # property text modification
            if display_item.changed():
                if display == xxxDisplay.NONE:
                    changes.append(PropertyTextChangeDelete(name))
                elif display_item.initial() == xxxDisplay.NONE:
                    pt_args = self._getRowPropertyTextItemValues(row_idx)
                    if pt_args is not None:
                        changes.append(PropertyTextChangeAdd(
                            name, display == xxxDisplay.SHOW, *pt_args
                        ))
                else:
                    pt_args = self._getRowPropertyTextItemValueDeltas(row_idx)
                    if pt_args is not None:
                        changes.append(PropertyTextChangeModify(
                            name, display == xxxDisplay.SHOW, *pt_args
                        ))
        return changes

    def _getItem(
        self    : Self,
        row_idx : int,
        col_idx : int
    ) -> PropertiesItem | None:
        item = self._table_model.item(row_idx, col_idx)
        return None if not isinstance(item, PropertiesItem) else item

    def _onSelectionChanged(
        self       : Self,
        selected   : QItemSelection,
        deselected : QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            index = None
        elif len(indexes) == 1:
            index = indexes[0]
        else:
            raise ValueError("Multiple indexes selected") # should never happen
        if index is None:
            # no row selected
            en_del_prop = False
            en_add_text = False
            en_del_text = False
        elif index.parent().isValid():
            # child (property text) row selected
            en_del_prop = False
            en_add_text = True
            en_del_text = True
        else:
            # parent (property) row selected
            en_del_prop = True
            en_add_text = True
            pt_col0_name = list(_PT_COLS.keys())[0]
            pt_col0_col = _COLS.index(pt_col0_name)
            pt_col0_idx = index.siblingAtColumn(pt_col0_col)
            pt_col0_item = self._table_model.itemFromIndex(pt_col0_idx)
            en_del_text = isinstance(pt_col0_item, PropertiesItem) \
                and not pt_col0_item.deleted()
        self._del_prop_button.setEnabled(en_del_prop)
        self._add_text_button.setEnabled(en_add_text)
        self._del_text_button.setEnabled(en_del_text)
        self._selected_index = index

    def _onKindChanged(
        self    : Self,
        kind    : DataKind,
        row_idx : int
    ) -> None:
        value_col = _COLS.index("Value")
        if (value_item := self._getItem(row_idx, value_col)) is None:
            logger().error(f"Bad value item for row {row_idx}")
            return
        value_item.setKind(kind)

    def _onDisplayChanged(
        self    : Self,
        display : xxxDisplay,
        row_idx : int
    ) -> None:
        item = self._obj
        pt_new = False
        for col_name, (kind, value, _) in _PT_COLS.items():
            col_idx = _COLS.index(col_name)
            if (pt_item := self._getItem(row_idx, col_idx)) is None:
                logger().error(f"Bad PT item for row {row_idx}")
                continue
            if pt_item is not None and col_name == "Cleat":
                pt_new = pt_item.new()
            if display != xxxDisplay.NONE and pt_item is None:
                if not isinstance(item, ItemHandlesMixin):
                    raise TypeError("Bad item")
                if col_name == "Cleat":
                    kind = _HANDLE_KIND[item.handleIdType()]
                    value = list(item.handles().keys())[0]
                pt_item = PropertiesItem(
                    kind=kind, value=value, new=True
                )
                self._table_model.setItem(row_idx, col_idx, pt_item)
                pt_new = True
            if pt_item is not None:
                pt_item.setEnabled(display != xxxDisplay.NONE or not pt_new)
                pt_item.setEditable(display != xxxDisplay.NONE)
                pt_item.setDeleted(display == xxxDisplay.NONE and not pt_new)

    def _refreshDisplay(self : Self, row_idx : int) -> None:
        """Refresh PT columns from the model's Display value."""
        display_col = _COLS.index("Display")
        if not isinstance(display_item := self._table_model.item(row_idx, display_col), PropertiesItem):
            logger().error(f"Bad display item for row {row_idx}")
            return
        if not isinstance(display_value := display_item.value(), xxxDisplay):
            logger().error(f"Bad display value for row {row_idx}")
            return
        self._onDisplayChanged(display_value, row_idx)

    def _onDataChanged(
        self         : Self,
        top_left     : QModelIndex,
        bottom_right : QModelIndex,
        _roles       : list[int]
    ) -> None:
        """Handle display changes."""
        columns = range(
            top_left.column(), bottom_right.column() + 1
        )
        display_col = _COLS.index("Display")
        if display_col not in columns:
            return
        for row_idx in range(
            top_left.row(), bottom_right.row() + 1
        ):
            self._refreshDisplay(row_idx)

    def _buildPropertyRow(
        self   : Self,
        name   : str,
        custom : bool,
        kind   : DataKind,
        value  : Any,
        pt     : PropertyTextItem | None = None,
        *,
        new    : bool = False
    ) -> list[ChangeItem | PropertiesItem | None]:
        row : list[ChangeItem | PropertiesItem | None] = []
        if new:
            row.append(NewPropertyChangeItem(NewChange.ADD))
        else:
            row.append(ExistingPropertyChangeItem(ExistingChange.NO_CHANGE))
        row.append(PropertiesItem(DataKind.STR, name))
        row.append(PropertiesItem(DataKind.BOOL, custom))
        row.append(PropertiesItem(DataKind.KIND, kind))
        row.append(PropertiesItem(kind, value))
        if pt is None:
            row.append(NewPropertyTextChangeItem(NewChange.NONE))
            row += [None] * len(_PT_COLS)
        else:
            row.append(ExistingPropertyTextChangeItem(ExistingChange.NO_CHANGE))
            row += self._propertyTextFields(pt)
        return row

    def _propertyTextFields(
        self : Self,
        pt : PropertyTextItem
    ) -> list[ChangeItem | PropertiesItem | None]:
        return [
            PropertiesItem(kind, method(pt))
            for (kind, _default, method) in _PT_COLS.values()
        ]

    def _buildPropertyTextRow(
        self : Self,
        pt : PropertyTextItem
    ) -> list[ChangeItem | PropertiesItem | None]:
        row : list[ChangeItem | PropertiesItem | None] = []
        row += [None] * (1 + len(_PROP_COLS))
        row.append(ExistingPropertyTextChangeItem(ExistingChange.NO_CHANGE))
        row += self._propertyTextFields(pt)
        return row

    def _addProperty(self : Self) -> None:
        """Add a new property."""
        model = self._table_model
        row_idx = model.rowCount()
        row = self._buildPropertyRow("", True, DataKind.STR, "", new=True)
        model.appendRow(row)
        self._refreshTable()
        self._table_view.setCurrentIndex(model.index(row_idx, 0))
        self._table_view.edit(model.index(row_idx, _COLS.index("Name")))

    def _delProperty(self : Self) -> None:
        """Delete the selected property, and any associated texts."""
        if self._selected_index is None:
            logger().error("No selection")
            return
        row_idx = self._selected_index.row()
        if (name_item := self._getItem(row_idx, 0)) is None:
            logger().error(f"Bad name item for row {row_idx}")
            return
        if name_item.deleted():
            logger().error(f"Property {name} already deleted")
            return

        if not isinstance(name := name_item.value(), str):
            logger().error(f"Name is not a string: {name}")
            return
        selected_index = self._selectedIndex(selected)

    def _deleteRows(self : Self) -> None:
        # get all selected rows
        rows = self._selectedRows()
        # delete rows
        failures = []
        for row in rows:
            if (name_item := self._getItem(row, 0)) is None:
                logger().error(f"Bad name item for row {row}")
                continue
            if not isinstance(name := name_item.value(), str):
                logger().error(f"Name is not a string: {name}")
                continue
            if name not in self._obj.properties \
            or not self._obj.propertyInherent(name):
                for col_idx in range(self._table_model.columnCount()):
                    item = self._getItem(row, col_idx)
                    if item is not None:
                        item.setDeleted(True)
            else:
                failures.append(name_item.text())
        # report failures if any
        if failures:
            msg = "The following properties could not be deleted:\n"
            msg += ", ".join(failures)
            QMessageBox.warning(self, "Property Deletion Failure", msg)

    def _getValueColumnWidth(self : Self) -> int:
        from ..components.combo.color       import ColorComboBox
        from ..components.combo.line_width  import LineWidthComboBox
        from ..components.combo.line_style  import LineStyleComboBox
        from ..components.combo.fill_style  import FillStyleComboBox
        from ..components.combo.font_family import FontFamilyComboBox
        from ..components.combo.font_size   import FontSizeComboBox
        from ..components.combo.font_bool   import FontBoolComboBox
        max_width = 50  # minimum width
        # get all font families, sorted by name length
        families = sorted(QFontDatabase.families(), key=len)
        test_editors = [
            ColorComboBox     (None, QColor("#FFFFFF"), None),
            LineWidthComboBox (None, 8.0, None),
            LineStyleComboBox (None, Qt.PenStyle.DashDotDotLine, None),
            FillStyleComboBox (None, Qt.BrushStyle.DiagCrossPattern, None),
            FontFamilyComboBox(None, families[-1], None),
            FontSizeComboBox  (None, 888.8, None),
            FontBoolComboBox  (None, False, None)
        ]
        for editor in test_editors:
            hint = editor.sizeHint()
            max_width = max(max_width, hint.width())
            editor.deleteLater()
        return max_width + 20  # padding

    def _selectedRows(self : Self) -> list[int]:
        # get all selected row indices
        if not isinstance(selection_model := self._table_view.selectionModel(), QItemSelectionModel):
            logger().error("Bad selection model")
            return []
        indices = selection_model.selectedRows()
        # extract row numbers
        rows = [index.row() for index in indices]
        # sort in reverse order to avoid index shifting issues when deleting
        rows.sort(reverse=True)
        # done
        return rows

    def _getRowPropertyTextItems(
        self    : Self,
        row_idx : int
    ) -> None | tuple[
        PropertiesItem,  # Cleat
        PropertiesItem,  # X
        PropertiesItem,  # Y
        PropertiesItem,  # Rotation
        PropertiesItem,  # Mirror H
        PropertiesItem,  # Mirror V
        PropertiesItem,  # Auto Flip
        PropertiesItem,  # Origin
        PropertiesItem,  # Align H
        PropertiesItem,  # Align V
        PropertiesItem,  # Width
        PropertiesItem,  # Height
        PropertiesItem,  # Color
        PropertiesItem,  # Font
        PropertiesItem,  # Size
        PropertiesItem,  # Bold
        PropertiesItem,  # Italic
        PropertiesItem   # Underline
    ]:
        # get items
        cleat_item     = self._getItem(row_idx, _COLS.index("Cleat")),
        x_item         = self._getItem(row_idx, _COLS.index("X")),
        y_item         = self._getItem(row_idx, _COLS.index("Y")),
        rotation_item  = self._getItem(row_idx, _COLS.index("Rotation")),
        mirror_h_item  = self._getItem(row_idx, _COLS.index("Mirror H")),
        mirror_v_item  = self._getItem(row_idx, _COLS.index("Mirror V")),
        autoflip_item  = self._getItem(row_idx, _COLS.index("Auto Flip")),
        origin_item    = self._getItem(row_idx, _COLS.index("Origin")),
        align_h_item   = self._getItem(row_idx, _COLS.index("Align H")),
        align_v_item   = self._getItem(row_idx, _COLS.index("Align V")),
        width_item     = self._getItem(row_idx, _COLS.index("Width")),
        height_item    = self._getItem(row_idx, _COLS.index("Height")),
        color_item     = self._getItem(row_idx, _COLS.index("Color")),
        font_item      = self._getItem(row_idx, _COLS.index("Font")),
        size_item      = self._getItem(row_idx, _COLS.index("Size")),
        bold_item      = self._getItem(row_idx, _COLS.index("Bold")),
        italic_item    = self._getItem(row_idx, _COLS.index("Italic")),
        underline_item = self._getItem(row_idx, _COLS.index("Underline"))
        if not isinstance(cleat_item, PropertiesItem) \
        or not isinstance(x_item, PropertiesItem) \
        or not isinstance(y_item, PropertiesItem) \
        or not isinstance(rotation_item, PropertiesItem) \
        or not isinstance(mirror_h_item, PropertiesItem) \
        or not isinstance(mirror_v_item, PropertiesItem) \
        or not isinstance(autoflip_item, PropertiesItem) \
        or not isinstance(origin_item, PropertiesItem) \
        or not isinstance(align_h_item, PropertiesItem) \
        or not isinstance(align_v_item, PropertiesItem) \
        or not isinstance(width_item, PropertiesItem) \
        or not isinstance(height_item, PropertiesItem) \
        or not isinstance(color_item, PropertiesItem) \
        or not isinstance(font_item, PropertiesItem) \
        or not isinstance(size_item, PropertiesItem) \
        or not isinstance(bold_item, PropertiesItem) \
        or not isinstance(italic_item, PropertiesItem) \
        or not isinstance(underline_item, PropertiesItem):
            return None
        return (
            cleat_item,
            x_item,
            y_item,
            rotation_item,
            mirror_h_item,
            mirror_v_item,
            autoflip_item,
            origin_item,
            align_h_item,
            align_v_item,
            width_item,
            height_item,
            color_item,
            font_item,
            size_item,
            bold_item,
            italic_item,
            underline_item
        )

    def _getRowPropertyTextItemValues(
        self    : Self,
        row_idx : int,
        items   : tuple | None = None
    ) -> None | tuple[
        HandleId,      # Cleat
        float,         # X
        float,         # Y
        float,         # Rotation
        bool,          # Mirror H
        bool,          # Mirror V
        bool,          # Auto Flip
        RectHandleId,  # Origin
        AlignH,        # Align H
        AlignV,        # Align V
        float,         # Width
        float,         # Height
        QColor,        # Color
        str,           # Font
        float,         # Size
        bool,          # Bold
        bool,          # Italic
        bool,          # Underline
    ]:
        # get items
        if items is None:
            items = self._getRowPropertyTextItems(row_idx)
        if items is None:
            return None
        cleat_item     , \
        x_item         , \
        y_item         , \
        rotation_item  , \
        mirror_h_item  , \
        mirror_v_item  , \
        autoflip_item  , \
        origin_item    , \
        align_h_item   , \
        align_v_item   , \
        width_item     , \
        height_item    , \
        color_item     , \
        font_item      , \
        size_item      , \
        bold_item      , \
        italic_item    , \
        underline_item = items
        # values
        cleat     = cleat_item     .value()
        x         = x_item         .value()
        y         = y_item         .value()
        rotation  = rotation_item  .value()
        mirror_h  = mirror_h_item  .value()
        mirror_v  = mirror_v_item  .value()
        autoflip  = autoflip_item  .value()
        origin    = origin_item    .value()
        align_h   = align_h_item   .value()
        align_v   = align_v_item   .value()
        width     = width_item     .value()
        height    = height_item    .value()
        color     = color_item     .value()
        font      = font_item      .value()
        size      = size_item      .value()
        bold      = bold_item      .value()
        italic    = italic_item    .value()
        underline = underline_item .value()
        # check values
        if not isinstance(cleat,     HandleId     ) \
        or not isinstance(x,         float        ) \
        or not isinstance(y,         float        ) \
        or not isinstance(rotation,  float        ) \
        or not isinstance(mirror_h,  bool         ) \
        or not isinstance(mirror_v,  bool         ) \
        or not isinstance(autoflip,  bool         ) \
        or not isinstance(origin,    RectHandleId ) \
        or not isinstance(align_h,   AlignH       ) \
        or not isinstance(align_v,   AlignV       ) \
        or not isinstance(width,     float        ) \
        or not isinstance(height,    float        ) \
        or not isinstance(color,     QColor       ) \
        or not isinstance(font,      str          ) \
        or not isinstance(size,      float        ) \
        or not isinstance(bold,      bool         ) \
        or not isinstance(italic,    bool         ) \
        or not isinstance(underline, bool         ):
            return None
        # done
        return (
            cleat,
            x,
            y,
            rotation,
            mirror_h,
            mirror_v,
            autoflip,
            origin,
            align_h,
            align_v,
            width,
            height,
            color,
            font,
            size,
            bold,
            italic,
            underline
        )

    def _getRowPropertyTextItemValueDeltas(
        self    : Self,
        row_idx : int
    ) -> None | tuple[
        NoChange | HandleId,      # Cleat
        NoChange | float,         # X
        NoChange | float,         # Y
        NoChange | float,         # Rotation
        NoChange | bool,          # Mirror H
        NoChange | bool,          # Mirror V
        NoChange | bool,          # Auto Flip
        NoChange | RectHandleId,  # Origin
        NoChange | AlignH,        # Align H
        NoChange | AlignV,        # Align V
        NoChange | float,         # Width
        NoChange | float,         # Height
        NoChange | QColor,        # Color
        NoChange | str,           # Font
        NoChange | float,         # Size
        NoChange | bool,          # Bold
        NoChange | bool,          # Italic
        NoChange | bool,          # Underline
    ]:
        # get items
        if (items := self._getRowPropertyTextItems(row_idx)) is None:
            return None
        cleat_item     , \
        x_item         , \
        y_item         , \
        rotation_item  , \
        mirror_h_item  , \
        mirror_v_item  , \
        autoflip_item  , \
        origin_item    , \
        align_h_item   , \
        align_v_item   , \
        width_item     , \
        height_item    , \
        color_item     , \
        font_item      , \
        size_item      , \
        bold_item      , \
        italic_item    , \
        underline_item = items
        # get values
        if (values := self._getRowPropertyTextItemValues(row_idx, items)) is None:
            return None
        cleat     , \
        x         , \
        y         , \
        rotation  , \
        mirror_h  , \
        mirror_v  , \
        autoflip  , \
        origin    , \
        align_h   , \
        align_v   , \
        width     , \
        height    , \
        color     , \
        font      , \
        size      , \
        bold      , \
        italic    , \
        underline = values
        # allow for no change
        if not cleat_item     .changed() : cleat     = NO_CHANGE
        if not x_item         .changed() : x         = NO_CHANGE
        if not y_item         .changed() : y         = NO_CHANGE
        if not rotation_item  .changed() : rotation  = NO_CHANGE
        if not mirror_h_item  .changed() : mirror_h  = NO_CHANGE
        if not mirror_v_item  .changed() : mirror_v  = NO_CHANGE
        if not autoflip_item  .changed() : autoflip  = NO_CHANGE
        if not origin_item    .changed() : origin    = NO_CHANGE
        if not align_h_item   .changed() : align_h   = NO_CHANGE
        if not align_v_item   .changed() : align_v   = NO_CHANGE
        if not width_item     .changed() : width     = NO_CHANGE
        if not height_item    .changed() : height    = NO_CHANGE
        if not color_item     .changed() : color     = NO_CHANGE
        if not font_item      .changed() : font      = NO_CHANGE
        if not size_item      .changed() : size      = NO_CHANGE
        if not bold_item      .changed() : bold      = NO_CHANGE
        if not italic_item    .changed() : italic    = NO_CHANGE
        if not underline_item .changed() : underline = NO_CHANGE
        # done
        return (
            cleat,
            x,
            y,
            rotation,
            mirror_h,
            mirror_v,
            autoflip,
            origin,
            align_h,
            align_v,
            width,
            height,
            color,
            font,
            size,
            bold,
            italic,
            underline
        )

    def _refreshTable(self : Self) -> None:
        # refresh entire table
        if self._table_model.rowCount() > 0:
            top_left = self._table_model.index(0, 0)
            bottom_right = self._table_model.index(
                self._table_model.rowCount() - 1,
                self._table_model.columnCount() - 1
            )
            self._onDataChanged(top_left, bottom_right, [])
