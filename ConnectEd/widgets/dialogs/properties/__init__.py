from typing      import Self, Any, TypeAlias

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView, QStyledItemDelegate, \
                            QGraphicsItem
from PyQt6.QtGui     import QStandardItemModel, QColor, QFontDatabase

from ....core.types import DEFAULT, AlignH, AlignV, Text, \
                           HandleId, RectHandleId

from ...graphics.properties import PropertyDisplay, \
                                   PropertyAdd, PropertyEdit, PropertyDelete

from ...graphics.items.mixin.handle import ItemHandlesMixin

from ..components.table_view import TableView

from .item import PropertiesItem

from .delegate import PropertiesDelegate

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.properties          import PropertiesMixin
    from ...graphics.views.drawing       import DrawingView


_HEADERS = [
    "Name"      ,
    "Value"     ,
    "Display"   ,
    "Cleat"     ,
    "X"         ,
    "Y"         ,
    "Origin"    ,
    "AlignH"    ,
    "AlignV"    ,
    "Width"     ,
    "Height"    ,
    "Color"     ,
    "Family"    ,
    "Size"      ,
    "Bold"      ,
    "Italic"    ,
    "Underline"
]


class PropertiesDialog(QDialog):
    ItemType : TypeAlias = \
        "QGraphicsItem | ItemHandlesMixin[HandleId] | PropertiesMixin"

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
    _deletions      : list[str]  # names of properties to delete

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
        self._table_model.setHorizontalHeaderLabels(_HEADERS)
        # add rows
        for name in item.getPropertyNames():
            self._table_model.appendRow(self._buildRow(name))
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
        self._deletions = []

    def getEdits(self : Self) -> list[PropertyAdd | PropertyEdit | PropertyDelete]:
        edits : list[PropertyAdd | PropertyEdit | PropertyDelete] = []
        # process deletions
        for name in self._deletions:
            edits.append(PropertyDelete(name))
        # process additions and modifications
        after_names : list[str] = []
        for row in range(self._table_model.rowCount()):
            row_items : list[PropertiesItem] = [
                self._table_model.item(row, col) \
                    for col in range(self._table_model.columnCount())
            ]
            row_values : list[Any] = [item.value() for item in row_items]
            after_name = row_values[0]
            if after_name in after_names:
                QMessageBox.warning(
                    self,
                    "Property Name Duplicated",
                    f"Property '{after_name}' appears multiple times"
                )
                continue  # skip duplicate
            after_names.append(after_name)
            name_item = row_items[0]
            before_name = name_item.initial()
            if before_name is None:
                edit = PropertyAdd(*row_values)
            else:
                name = (before_name, after_name) if before_name != after_name \
                    else before_name
                edit = PropertyEdit(name, *row_values[1:])
            edits.append(edit)
        return edits

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
                item : PropertiesItem = self._table_model.item(row_idx, col_idx)
                if item is None:
                    continue
                if col_idx > 2:
                    item.setEnabled(display != PropertyDisplay.NONE)

    def _buildRow(self : Self, name : str) -> list[PropertiesItem]:
        item = self._item
        new = not item.hasProperty(name)
        pt = item.getPropertyText(name)
        pt_new_enabled = { "new" : pt is None, "enabled" : pt is not None }
        row = [
            # Name
            PropertiesItem(
                kind     = "str",
                value    = name,
                new      = new,
                editable = new or not item.isPropertyInherent(name)
            ),
            # Value
            PropertiesItem(
                kind     = "Text" if new else item.getPropertyKind(name),
                value    = Text("", False) if new else item.getPropertyValue(name),
                default  = None if new else item.getPropertyDefault(name),
                new      = new,
                editable = new or not item.isPropertyReadOnly(name)
            ),
            # Display
            PropertiesItem(
                kind  = "Display",
                value = item.getPropertyDisplay(name),
                new   = new
            ),
            # Cleat
            PropertiesItem(
                kind  = item.handleIdType().__name__,
                value = list(item.handles().keys())[0] if pt is None else pt.cleat(),
                **pt_new_enabled
            ),
            # X
            PropertiesItem(
                kind  = "float",
                value = 0.0 if pt is None else pt.x(),
                **pt_new_enabled
            ),
            # Y
            PropertiesItem(
                kind    = "float",
                value   = 0.0 if pt is None else pt.y(),
                **pt_new_enabled
            ),
            # Origin
            PropertiesItem(
                kind  = "RectHandleId",
                value = RectHandleId.TOP_LEFT if pt is None else pt.origin(),
                **pt_new_enabled
            ),
            # AlignH
            PropertiesItem(
                kind  = "AlignH",
                value = AlignH.LEFT if pt is None else pt.alignH(),
                **pt_new_enabled
            ),
            # AlignV
            PropertiesItem(
                kind  = "AlignV",
                value = AlignV.TOP if pt is None else pt.alignV(),
                **pt_new_enabled
            ),
            # Width
            PropertiesItem(
                kind  = "float",
                value = -1.0 if pt is None else pt.width(),
                **pt_new_enabled
            ),
            # Height
            PropertiesItem(
                kind  = "float",
                value = -1.0 if pt is None else pt.height(),
                **pt_new_enabled
            ),
            # Color
            PropertiesItem(
                kind  = "Color",
                value = DEFAULT if pt is None else pt.color(),
                **pt_new_enabled
            ),
            # Family
            PropertiesItem(
                kind  = "FontFamily",
                value = DEFAULT if pt is None else pt.quillFamily(),
                **pt_new_enabled
            ),
            # Size
            PropertiesItem(
                kind  = "FontSize",
                value = DEFAULT if pt is None else pt.quillSize(),
                **pt_new_enabled
            ),
            # Bold
            PropertiesItem(
                kind  = "FontBool",
                value = DEFAULT if pt is None else pt.quillBold(),
                **pt_new_enabled
            ),
            # Italic
            PropertiesItem(
                kind  = "FontBool",
                value = DEFAULT if pt is None else pt.quillItalic(),
                **pt_new_enabled
            ),
            # Underline
            PropertiesItem(
                kind  = "FontBool",
                value = DEFAULT if pt is None else pt.quillUnderline(),
                **pt_new_enabled
            )
        ]
        return row

    def _addRow(self : Self) -> None:
        """Add a new property."""
        row_idx = self._table_model.rowCount()
        self._table_model.appendRow(self._buildRow(""))
        self._refreshTable()
        self._table_view.setCurrentIndex(self._table_model.index(row_idx, 0))
        self._table_view.edit(self._table_model.index(row_idx, 0))

    def _deleteRows(self : Self) -> None:
        # get all selected rows
        rows = self._selectedRows()
        # delete rows
        failures = []
        for row in rows:
            name_item : PropertiesItem = self._table_model.item(row, 0)
            if name_item.isEditable():
                before_name = name_item.initial()
                if before_name is not None:  # pre-exising row
                    self._deletions.append(before_name)
                self._table_model.removeRow(row)
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

    def _refreshTable(self : Self) -> None:
        # refresh entire table
        if self._table_model.rowCount() > 0:
            top_left = self._table_model.index(0, 0)
            bottom_right = self._table_model.index(
                self._table_model.rowCount() - 1,
                self._table_model.columnCount() - 1
            )
            self._onDataChanged(top_left, bottom_right, [])
