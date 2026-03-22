from typing      import Self, Any, TypeAlias
from enum        import Enum

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView, QGraphicsItem
from PyQt6.QtGui     import QStandardItemModel, QColor, QFontDatabase

from ....core.types import (
    DEFAULT,
    RectHandleId, LineHandleId, BlockPinHandleId, SymbolPinHandleId, \
    DataKind, Display
)

from ....core.utils import pascal2snake

from ...graphics.items.mixin.handle import ItemHandlesMixin

from ..components.table_view import TableView

from ..new_property import NewPropertyDialog

from .item import PropertiesItem

from .delegate import PropertiesDelegate

from .types import (
    PropertyChangeAdd, PropertyChangeModify, PropertyChangeDelete,
    PropertyChangeTextAdd, PropertyChangeTextModify, PropertyChangeTextDelete,
    PropertyChangeType
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.properties          import PropertiesMixin
    from ...graphics.views.drawing       import DrawingView


_PT_COLS : dict[str, DataKind] = {
#                   kind                   method name
    "Cleat"     : ( None                 , "cleat"          ),
    "X"         : ( DataKind.FLOAT       , "x"              ),
    "Y"         : ( DataKind.FLOAT       , "y"              ),
    "Rotation"  : ( DataKind.ROTATION    , "rotation"       ),
    "Flip"      : ( DataKind.BOOL        , "flip"           ),
    "Origin"    : ( DataKind.RECT_HANDLE , "origin"         ),
    "AlignH"    : ( DataKind.ALIGN_H     , "alignH"         ),
    "AlignV"    : ( DataKind.ALIGN_V     , "alignV"         ),
    "Width"     : ( DataKind.FLOAT       , "width"          ),
    "Height"    : ( DataKind.FLOAT       , "height"         ),
    "Color"     : ( DataKind.COLOR       , "quillColor"     ),
    "Family"    : ( DataKind.FONT_FAMILY , "quillFamily"    ),
    "Size"      : ( DataKind.FONT_SIZE   , "quillSize"      ),
    "Bold"      : ( DataKind.FONT_BOOL   , "quillBold"      ),
    "Italic"    : ( DataKind.FONT_BOOL   , "quillItalic"    ),
    "Underline" : ( DataKind.FONT_BOOL   , "quillUnderline" )
}


_COLS : list[str] = ["Name", "Value", "Display"] + list(_PT_COLS.keys())


_HANDLE_KIND : dict[type, DataKind] = {
    RectHandleId      : DataKind.RECT_HANDLE,
    LineHandleId      : DataKind.LINE_HANDLE,
    BlockPinHandleId  : DataKind.BLOCK_PIN_HANDLE,
    SymbolPinHandleId : DataKind.SYMBOL_PIN_HANDLE
}


class PropertiesDialog(QDialog):
    ItemType : TypeAlias = \
        "QGraphicsItem | ItemHandlesMixin | PropertiesMixin"

    _item           : PropertiesMixin
    _dialog_layout  : QVBoxLayout
    _table_model    : QStandardItemModel
    _table_view     : TableView
    _button_layout  : QHBoxLayout
    _display_button : QPushButton
    _add_button     : QPushButton
    _delete_button  : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton
    _delegates      : list[PropertiesDelegate]

    def __init__(
        self : Self,
        item : ItemType,
        view : "DrawingView | None" = None
    ) -> None:
        # initialise
        self._item = item
        super().__init__(view)
        item_name = item.__class__.__name__.removesuffix("Item")
        self.setWindowTitle(f"{item_name} Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # create model
        self._table_model = QStandardItemModel()
        # set headers
        self._table_model.setHorizontalHeaderLabels(_COLS)
        # add rows
        for name in item.properties.names():
            self._table_model.appendRow(self._buildRow(
                name,
                item.properties.kind(name),
                item.properties.value(name)
            ))
        # create table view
        self._table_view = TableView(self._table_model)
        # create and assign delegates (must keep references to prevent GC)
        self._delegates = []
        for col_idx in range(self._table_model.columnCount()):
            delegate = PropertiesDelegate()
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
        # open persistent editors for bool cells (show checkboxes)
        self._openPersistentEditors()
        # resize columns
        self._table_view.resizeColumnsToContents()
        self._table_view.setColumnWidth(1, self._getValueColumnWidth())
        # build button layout
        self._button_layout = QHBoxLayout()
        self._add_button = QPushButton("New")
        self._add_button.clicked.connect(self._addRow)
        self._button_layout.addWidget(self._add_button)
        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._deleteRows)
        self._button_layout.addWidget(self._delete_button)
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
        min_width = self._table_view.horizontalHeader().length() + 50
        min_height = self._table_view.verticalHeader().length() + 50
        self.setMinimumSize(min_width, min_height)
        self._table_model.dataChanged.connect(self._onDataChanged)

    def getChanges(self : Self) -> list[PropertyChangeType]:
        """
        Returns a list of changes to be applied to the item.
        """
        changes : list[PropertyChangeType] = []
        # deletions
        for row_idx in range(self._table_model.rowCount()):
            name_item : PropertiesItem = self._table_model.item(row_idx, 0)
            if name_item.deleted():
                name = name_item.value()
                changes.append(PropertyChangeDelete(name))
        # renames
        for row_idx in range(self._table_model.rowCount()):
            name_item : PropertiesItem = self._table_model.item(row_idx, 0)
            if name_item.changed():
                name = name_item.initial()
                rename = name_item.value()
                changes.append(PropertyChangeRename(name, rename))
        # additions
        for row_idx in range(self._table_model.rowCount()):
            name_item : PropertiesItem | None = self._table_model.item(row_idx, 0)
            if name_item.new():
                name = name_item.value()
                value_item : PropertiesItem = self._table_model.item(
                    row_idx, _COLS.index("Value")
                )
                kind = value_item.kind()
                value = value_item.value()
                changes.append(PropertyChangeAdd(name, kind, value))
                # property text item
                display_item : PropertiesItem | None = self._table_model.item(
                    row_idx, _COLS.index("Display")
                )
                display = display_item.value()
                if display != Display.NONE:
                    pt_args = self._getPropertyTextArgs(row_idx)
                    changes.append(PropertyChangeTextAdd(**pt_args))
        # modifications
        for row_idx in range(self._table_model.rowCount()):
            # property
            name_item : PropertiesItem | None = self._table_model.item(row_idx, 0)
            name = name_item.value()
            value_item : PropertiesItem = self._table_model.item(
                row_idx, _COLS.index("Value")
            )
            if value_item.changed():
                changes.append(PropertyChangeModify(
                    name  = name,
                    kind  = value_item.kind(),
                    value = value_item.value()
                ))
            # property text item
            display_item = self._table_model.item(row_idx, _COLS.index("Display"))
            if not display_item.changed():
                continue
            display_old = display_item.initial()
            display_new = display_item.value()
            pt_args = {"name": name, **self._getPropertyTextArgs(row_idx)}
            if display_new == Display.NONE:
                pt_args = {"name": name}
                property_change_cls = PropertyChangeTextDelete
            elif display_old == Display.NONE:
                property_change_cls = PropertyChangeTextAdd
            else:
                pt_args["visible"] = display_new == Display.SHOW
                property_change_cls = PropertyChangeTextModify
            changes.append(property_change_cls(**pt_args))
        return changes

    def _onDataChanged(
        self         : Self,
        top_left     : QModelIndex,
        bottom_right : QModelIndex,
        _roles       : list[int]
    ) -> None:
        """Highlight changed cells. Handle display choices."""
        # process rows
        for row_idx in range(top_left.row(), bottom_right.row() + 1):
            # ensure all columns to the right of the display column are
            # processed if the display column is being changed
            right_column = bottom_right.column()
            if 2 in range(top_left.column(), bottom_right.column() + 1):
                right_column = self._table_model.columnCount() - 1
            display_item : PropertiesItem = self._table_model.item(row_idx, 2)
            display = display_item.value()
            for col_idx in range(top_left.column(), right_column + 1):
                item : PropertiesItem | None = self._table_model.item(row_idx, col_idx)
                if item is None:
                    continue
                if col_idx > 2:
                    item.setEnabled(display != Display.NONE)

    def _buildRow(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> list[PropertiesItem]:
        item = self._item
        new = not item.properties.has(name)
        pt = item.properties.text(name)
        display = \
            Display.NONE if pt is None else \
            Display.SHOW if pt.isVisible() else \
            Display.HIDE
        pt_args = {
            "owner"   : item,
            "new"     : new,
            "enabled" : pt is not None
        }
        row = [
            # Name
            PropertiesItem(
                owner    = item,
                kind     = DataKind.STR,
                value    = name,
                new      = new,
                editable = new or not item.properties.inherent(name)
            ),
            # Value
            PropertiesItem(
                owner    = item,
                kind     = kind if new else item.properties.kind(name),
                value    = value if new else item.properties.value(name),
                default  = None if new else item.properties.default(name),
                new      = new,
                editable = new or item.properties.writeable(name)
            ),
            # Display
            PropertiesItem(
                owner = item,
                kind  = DataKind.DISPLAY,
                value = display,
                new   = new
            )
        ]
        for col_name, (kind, method_name) in _PT_COLS.items():
            if col_name == "Cleat":
                kind = _HANDLE_KIND[item.handleIdType()]
            row.append(PropertiesItem(
                kind  = kind,
                value = None if pt is None else getattr(pt, method_name)(),
                **pt_args
            ))
        return row

    def _addRow(self : Self) -> None:
        """Add a new property."""
        dialog = NewPropertyDialog(self)
        if dialog.exec():
            name = dialog.getName()
            kind = dialog.getKind()
            value = dialog.getValue()
            row_idx = self._table_model.rowCount()
            row = self._buildRow(name, kind, value)
            self._table_model.appendRow(row)
            self._refreshTable()  # why?
            self._table_view.setCurrentIndex(self._table_model.index(row_idx, 0))
            # finish up with value of new property being edited
            self._table_view.edit(self._table_model.index(
                row_idx, _COLS.index("Value")
            ))

    def _deleteRows(self : Self) -> None:
        # get all selected rows
        rows = self._selectedRows()
        # delete rows
        failures = []
        for row in rows:
            name_item : PropertiesItem = self._table_model.item(row, 0)
            name = name_item.value()
            if not self._item.properties.inherent(name):
                for col_idx in range(self._table_model.columnCount()):
                    item : PropertiesItem | None = self._table_model.item(row, col_idx)
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
            ColorComboBox     (DEFAULT, QColor("#FFFFFF"), None),
            LineWidthComboBox (DEFAULT, 8.0, None),
            LineStyleComboBox (DEFAULT, Qt.PenStyle.DashDotDotLine, None),
            FillStyleComboBox (DEFAULT, Qt.BrushStyle.DiagCrossPattern, None),
            FontFamilyComboBox(DEFAULT, families[-1], None),
            FontSizeComboBox  (DEFAULT, 888.8, None),
            FontBoolComboBox  (DEFAULT, False, None)
        ]
        for editor in test_editors:
            hint = editor.sizeHint()
            max_width = max(max_width, hint.width())
            editor.deleteLater()
        return max_width + 20  # padding

    def _selectedRows(self : Self) -> list[int]:
        # get all selected row indices
        indices = self._table_view.selectionModel().selectedRows()
        # extract row numbers
        rows = [index.row() for index in indices]
        # sort in reverse order to avoid index shifting issues when deleting
        rows.sort(reverse=True)
        # done
        return rows

    def _getPropertyTextArgs(self : Self, row_idx : int) -> dict[str, Any]:
        args = {}
        for col_name in _PT_COLS.keys():
            col_idx = _COLS.index(col_name)
            item : PropertiesItem | None = self._table_model.item(row_idx, col_idx)
            if item is not None and item.changed():
                arg_name = pascal2snake(col_name)
                args[arg_name] = item.value()
        return args

    def _openPersistentEditors(self : Self) -> None:
        for row in range(self._table_model.rowCount()):
            for col in range(self._table_model.columnCount()):
                item : PropertiesItem | None = \
                    self._table_model.item(row, col)
                if item is not None \
                and item.kind() == DataKind.BOOL:
                    item.clear()
                    idx = self._table_model.index(row, col)
                    self._table_view.openPersistentEditor(idx)

    def _refreshTable(self : Self) -> None:
        # refresh entire table
        if self._table_model.rowCount() > 0:
            top_left = self._table_model.index(0, 0)
            bottom_right = self._table_model.index(
                self._table_model.rowCount() - 1,
                self._table_model.columnCount() - 1
            )
            self._onDataChanged(top_left, bottom_right, [])
