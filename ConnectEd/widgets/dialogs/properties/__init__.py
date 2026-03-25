from typing import Self, Any, TypeAlias


from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView, QGraphicsItem
from PyQt6.QtGui     import QStandardItemModel, QColor, QFontDatabase

from ....app import logger

from ....core.types import (
    DEFAULT, Enable, AlignH, AlignV,
    RectHandleId, LineHandleId, BlockPinHandleId, SymbolPinHandleId, \
    DataKind, Display
)

from ....core.utils import pascal2snake

from ...graphics.items.mixin.handle import ItemHandlesMixin

from ..components.table_view import TableView

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
#                   kind                   default value              method name
    "Cleat"     : ( None                 , None                     , "cleat"          ), # noqa E501
    "X"         : ( DataKind.FLOAT       , 0.0                      , "x"              ), # noqa E501
    "Y"         : ( DataKind.FLOAT       , 0.0                      , "y"              ), # noqa E501
    "Rotation"  : ( DataKind.ROTATION    , 0.0                      , "rotation"       ), # noqa E501
    "Flip"      : ( DataKind.EN_DIS      , Enable.ENABLE            , "flip"           ), # noqa E501
    "Origin"    : ( DataKind.RECT_HANDLE , RectHandleId.BOTTOM_LEFT , "origin"         ), # noqa E501
    "AlignH"    : ( DataKind.ALIGN_H     , AlignH.LEFT              , "alignH"         ), # noqa E501
    "AlignV"    : ( DataKind.ALIGN_V     , AlignV.TOP               , "alignV"         ), # noqa E501
    "Width"     : ( DataKind.SIZE        , None                     , "width"          ), # noqa E501
    "Height"    : ( DataKind.SIZE        , None                     , "height"         ), # noqa E501
    "Color"     : ( DataKind.COLOR       , DEFAULT                  , "quillColor"     ), # noqa E501
    "Family"    : ( DataKind.FONT_FAMILY , DEFAULT                  , "quillFamily"    ), # noqa E501
    "Size"      : ( DataKind.FONT_SIZE   , DEFAULT                  , "quillSize"      ), # noqa E501
    "Bold"      : ( DataKind.FONT_BOOL   , DEFAULT                  , "quillBold"      ), # noqa E501
    "Italic"    : ( DataKind.FONT_BOOL   , DEFAULT                  , "quillItalic"    ), # noqa E501
    "Underline" : ( DataKind.FONT_BOOL   , DEFAULT                  , "quillUnderline" )  # noqa E501
}


_COLS : list[str] = ["Name", "Type", "Value", "Display"] + list(_PT_COLS.keys())


_HANDLE_KIND : dict[type, DataKind] = {
    RectHandleId      : DataKind.RECT_HANDLE,
    LineHandleId      : DataKind.LINE_HANDLE,
    BlockPinHandleId  : DataKind.BLOCK_PIN_HANDLE,
    SymbolPinHandleId : DataKind.SYMBOL_PIN_HANDLE
}


Cell = PropertiesItem | None


class PropertiesDialog(QDialog):
    ItemType : TypeAlias = \
        "QGraphicsItem | ItemHandlesMixin | PropertiesMixin"

    _item           : ItemType
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

    def accept(self : Self) -> None:
        name_col = _COLS.index("Name")
        kind_col = _COLS.index("Type")
        value_col = _COLS.index("Value")
        names : list[str] = []
        for row in range(self._table_model.rowCount()):
            # check for invalid or duplicate names
            name_item : PropertiesItem = self._table_model.item(row, name_col)
            new = name_item.new()
            if not name_item.deleted():
                name = name_item.value()
                if not name or name in names:
                    QMessageBox.warning(
                        self, "Invalid Property",
                        "Property names must be non-empty and unique."
                    )
                    index = self._table_model.index(row, name_col)
                    self._table_view.setCurrentIndex(index)
                    self._table_view.edit(index)
                    return
                names.append(name)
            # check for type/value mismatches on new properties
            kind_item : PropertiesItem = self._table_model.item(row, kind_col)
            if not kind_item.isEditable():
                continue
            kind = kind_item.value()
            value_item : PropertiesItem = self._table_model.item(row, value_col)
            print("kind:", kind, "value_item.kind():", value_item.kind())
            if kind != value_item.kind():
                print("type/value mismatch")
                logger().warning(f"Type/value mismatch for property '{name}'")
                value_item.setKind(kind)
            value = value_item.value()
            if not isinstance(value, kind.types()):
                QMessageBox.warning(
                    self, "Invalid Property",
                    f"Value of property '{name}' does not match type '{kind}'."
                )
                index = self._table_model.index(row, value_col)
                self._table_view.setCurrentIndex(index)
                self._table_view.edit(index)
                return
        super().accept()

    def getChanges(self : Self) -> list[PropertyChangeType]:
        """
        Returns a list of changes to be applied to the item.
        """
        model = self._table_model
        changes : list[PropertyChangeType] = []
        # deletions
        for row_idx in range(model.rowCount()):
            name_item : PropertiesItem = model.item(row_idx, 0)
            if name_item.deleted():
                name = name_item.value()
                changes.append(PropertyChangeDelete(name))
        # additions and modifications
        for row_idx in range(model.rowCount()):
            name_item    : Cell = model.item(row_idx, _COLS.index("Name"))
            kind_item    : Cell = model.item(row_idx, _COLS.index("Type"))
            value_item   : Cell = model.item(row_idx, _COLS.index("Value"))
            display_item : Cell = model.item(row_idx, _COLS.index("Display"))
            name    = name_item.value()
            kind    = kind_item.value()
            value   = value_item.value()
            display = display_item.value()
            if name_item.new():
                # addition
                changes.append(PropertyChangeAdd(name, kind, value))
                # property text
                if display != Display.NONE:
                    pt_args = self._getPropertyTextArgs(row_idx, delta=False)
                    pt_args["name"] = name
                    pt_args["visible"] = display == Display.SHOW
                    changes.append(PropertyChangeTextAdd(**pt_args))
            else:
                # modification
                if  name_item.changed() \
                or  kind_item.changed() \
                or  value_item.changed():
                    changes.append(PropertyChangeModify(name, kind, value))
                # property text modification
                pt_args = {"name": name, **self._getPropertyTextArgs(row_idx)}
                if display_item.changed():
                    if display == Display.NONE:
                        pt_args = {"name": name}
                        property_change_cls = PropertyChangeTextDelete
                    elif display_item.initial() == Display.NONE:
                        property_change_cls = PropertyChangeTextAdd
                        pt_args["visible"] = display == Display.SHOW
                    else:
                        property_change_cls = PropertyChangeTextModify
                        pt_args["visible"] = display == Display.SHOW
                    changes.append(property_change_cls(**pt_args))
                elif len(pt_args) > 1:
                    changes.append(PropertyChangeTextModify(**pt_args))
        return changes

    def _onKindChanged(
        self    : Self,
        kind    : DataKind,
        row_idx : int
    ) -> None:
        value_col = _COLS.index("Value")
        value_item : Cell = self._table_model.item(row_idx, value_col)
        value_item.setKind(kind)

    def _onDisplayChanged(
        self    : Self,
        display : Display,
        row_idx : int
    ) -> None:
        item = self._item
        pt_new = False
        for col_name, (kind, value, _) in _PT_COLS.items():
            col_idx = _COLS.index(col_name)
            pt_item : Cell = self._table_model.item(row_idx, col_idx)
            if pt_item is not None and col_name == "Cleat":
                pt_new = pt_item.new()
            if display != Display.NONE and pt_item is None:
                if col_name == "Cleat":
                    kind = _HANDLE_KIND[item.handleIdType()]
                    value = list(item.handles().keys())[0]
                pt_item = PropertiesItem(
                    owner=item, kind=kind, value=value, new=True
                )
                self._table_model.setItem(row_idx, col_idx, pt_item)
                pt_new = True
            if pt_item is not None:
                pt_item.setEnabled(display != Display.NONE or not pt_new)
                pt_item.setEditable(display != Display.NONE)
                pt_item.setDeleted(display == Display.NONE and not pt_new)

    def _refreshDisplay(self : Self, row_idx : int) -> None:
        """Refresh PT columns from the model's Display value."""
        display_col = _COLS.index("Display")
        display_item : Cell = self._table_model.item(row_idx, display_col)
        self._onDisplayChanged(display_item.value(), row_idx)

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

    def _buildRow(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> list[PropertiesItem]:
        item = self._item
        new = not item.properties.has(name)
        custom = new or not item.properties.inherent(name)
        str_or_text = kind == DataKind.STR or kind == DataKind.TEXT
        pt = None if new else item.properties.text(name)
        display = \
            Display.NONE if pt is None else \
            Display.SHOW if pt.isVisible() else \
            Display.HIDE
        row = [
            # Name
            PropertiesItem(
                owner    = item,
                kind     = DataKind.STR,
                value    = name,
                new      = new,
                editable = custom
            ),
            # Type
            PropertiesItem(
                owner    = item,
                kind     = DataKind.KIND,
                value    = kind,
                new      = new,
                editable = custom
            ),
            # Value
            PropertiesItem(
                owner    = item,
                kind     = kind if new else item.properties.kind(name),
                value    = value if new else item.properties.value(name),
                default  = None if new else item.properties.default(name),
                new      = new,
                editable = custom or item.properties.writeable(name)
            ),
            # Display
            PropertiesItem(
                owner = item,
                kind  = DataKind.DISPLAY,
                value = display,
                new   = new
            )
        ]
        for col_name, (kind, _default, method_name) in _PT_COLS.items():
            cell = None
            if pt is not None:
                if col_name == "Cleat":
                    kind = _HANDLE_KIND[pt.handleIdType()]
                value = getattr(pt, method_name)()
                if col_name == "Flip":
                    value = Enable.ENABLE if value else Enable.DISABLE
                cell = PropertiesItem(owner=item, kind=kind, value=value)
            row.append(cell)
        return row

    def _addRow(self : Self) -> None:
        """Add a new property."""
        row_idx = self._table_model.rowCount()
        row = self._buildRow("", DataKind.STR, "")
        self._table_model.appendRow(row)
        self._refreshTable()
        self._table_view.setCurrentIndex(self._table_model.index(row_idx, 0))
        self._table_view.edit(self._table_model.index(row_idx, _COLS.index("Name")))

    def _deleteRows(self : Self) -> None:
        # get all selected rows
        rows = self._selectedRows()
        # delete rows
        failures = []
        for row in rows:
            name_item : Cell = self._table_model.item(row, 0)
            name = name_item.value()
            if not self._item.properties.has(name) \
            or not self._item.properties.inherent(name):
                for col_idx in range(self._table_model.columnCount()):
                    item : Cell = self._table_model.item(row, col_idx)
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

    def _getPropertyTextArgs(
        self    : Self,
        row_idx : int,
        delta   : bool = True
    ) -> dict[str, Any]:
        args = {}
        for col_name in _PT_COLS.keys():
            col_idx = _COLS.index(col_name)
            item : Cell = self._table_model.item(row_idx, col_idx)
            if item is None:
                continue
            value = item.value()
            if col_name == "Width" or col_name == "Height":
                value = -1.0 if value is None else value
            elif col_name == "Flip":
                value = value == Enable.ENABLE
            if item.changed() or not delta:
                args[pascal2snake(col_name)] = value
        return args

    def _refreshTable(self : Self) -> None:
        # refresh entire table
        if self._table_model.rowCount() > 0:
            top_left : Cell = self._table_model.index(0, 0)
            bottom_right : Cell = self._table_model.index(
                self._table_model.rowCount() - 1,
                self._table_model.columnCount() - 1
            )
            self._onDataChanged(top_left, bottom_right, [])
