from typing      import Self, Any, TypeAlias

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView
from PyQt6.QtGui     import QBrush

from ...app import settings

from ...core.utils import snake2proper

from ..graphics.properties import PropertyDisplay, \
                                  PropertyState, PropertyChange, PropertyEdit

from ..graphics.items import DEFAULT, AlignH, AlignV

from ..graphics.items.mixin.handle import ItemRectHandlesMixin

from .components.model import BaseItem, BaseModel

from .components.table_view import TableView

from .components.combo.color      import ColorComboBox
from .components.combo.line_width import LineWidthComboBox
from .components.combo.line_style import LineStyleComboBox
from .components.combo.fill_style import FillStyleComboBox

from .components.delegate import DialogItemDelegate

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.properties    import PropertiesMixin
    from ..graphics.views.drawing import DrawingView


class ExistingItem(BaseItem):
    def __init__(
        self      : Self,
        value     : Any,
        type_name : str = "str",
        default   : Any = None,
        editable  : bool = True,
        enabled   : bool = True
    ) -> None:
        super().__init__(value, value, type_name, default, editable, enabled)


class NewItem(BaseItem):
    def __init__(
        self      : Self,
        value     : Any = "",
        type_name : str = "str",
        default   : Any = None,
        editable  : bool = True,
        enabled   : bool = True
    ) -> None:
        super().__init__(None, value, type_name, default, editable, enabled)


class PropertiesDialog(QDialog):
    ItemType : TypeAlias = "PropertiesMixin"

    _item           : ItemType
    _dialog_layout  : QVBoxLayout
    _table_model    : BaseModel
    _table_view     : TableView
    _delegate       : DialogItemDelegate
    _button_layout  : QHBoxLayout
    _display_button : QPushButton
    _add_button     : QPushButton
    _delete_button  : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton
    _deletions      : list[str]                 # names of properties to delete

    def __init__(
        self : Self,
        item : ItemType,
        view : "DrawingView | None" = None
    ) -> None:
        # initialise
        self._item = item
        super().__init__(view)
        self.setWindowTitle(f"{item.__class__.__name__} Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # build model, record initial state
        self._table_model = BaseModel()
        headers = [
            snake2proper(field_name) \
                for field_name in PropertyState.__dataclass_fields__.keys()
        ]
        self._table_model.setHorizontalHeaderLabels(headers)
        for name in item.getPropertyNames():
            state : PropertyState = PropertyState.fromProperty(item, name)
            inherent  = item.isPropertyInherent(name)
            type_name = item.getPropertyTypeName(name)
            default   = item.getPropertyDefault(name)
            read_only = item.isPropertyReadOnly(name)
            self._table_model.appendRow([
                ExistingItem(name, editable=inherent),
                ExistingItem(state.value, type_name, default, not read_only),
                ExistingItem(state.display   , "PropertyDisplay"),
                ExistingItem(state.cleat     , "str"            ),
                ExistingItem(state.x         , "float"          ),
                ExistingItem(state.y         , "float"          ),
                ExistingItem(state.origin    , "str"            ),
                ExistingItem(state.align_h   , "AlignH"         ),
                ExistingItem(state.align_v   , "AlignV"         ),
                ExistingItem(state.width     , "float"          ),
                ExistingItem(state.height    , "float"          ),
                ExistingItem(state.color     , "QColor"         ),
                ExistingItem(state.family    , "FontFamily"     ),
                ExistingItem(state.size      , "FontSize"       ),
                ExistingItem(state.bold      , "bool"           ),
                ExistingItem(state.italic    , "bool"           ),
                ExistingItem(state.underline , "bool"           )
            ])
        # create delegate
        self._delegate = DialogItemDelegate()
        self._delegate.destroyed.connect(
            lambda: self._onDelegateDestroyed("Value")
        )
        # build table view and assign delegate
        self._table_view = TableView(self._table_model)
        for column in range(len(headers)):
            self._table_view.setItemDelegateForColumn(column, self._delegate)
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
        self._add_button.clicked.connect(self._add)
        self._button_layout.addWidget(self._add_button)
        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._delete)
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

    def getEdits(self : Self) -> list[PropertyEdit]:
        edits : list[PropertyEdit] = []
        # process deletions
        for name in self._deletions:
            edits.append(PropertyEdit(name, None))
        # process additions and modifications
        after_names : list[str] = []
        # check for and ignore duplicates and anomalies
        for row in range(self._table_model.rowCount()):
            row_values = [
                self._table_model.item(row, col).getValue() \
                    for col in range(self._table_model.columnCount())
            ]
            after_name = row_values[0]
            # check for and skip duplicates
            if after_name in after_names:
                QMessageBox.warning(
                    self,
                    "Property Name Duplicated",
                    f"Property '{after_name}' appears multiple times"
                )
                continue  # skip duplicate
            after_names.append(after_name)
            # build changes; check for and ignore anomalies
            name_item : BaseItem = self._table_model.item(row, 0)
            before_name = name_item.getBefore()
            change_cls = PropertyState if before_name is None else PropertyChange
            change = PropertyEdit(before_name, change_cls(*row_values))
            edits.append(change)
        return edits

    def _onDelegateDestroyed(self : Self, _ : str) -> None:
        """Workaround to fix delegate lifecycle issue (silent crash)."""
        pass

    def _onDataChanged(
        self         : Self,
        top_left     : QModelIndex,
        bottom_right : QModelIndex,
        _roles       : list[int]
    ) -> None:
        """Highlight changed cells. Handle display choices."""
        from ..graphics.scenes.drawing import DrawingScene
        if settings().get("display/theme") == "dark":
            fg = Qt.GlobalColor.white
            bg_highlight = Qt.GlobalColor.darkYellow
        else:
            fg = Qt.GlobalColor.black
            bg_highlight = Qt.GlobalColor.yellow
        for row_idx in range(top_left.row(), bottom_right.row() + 1):
            # ensure all columns to the right of the display column are
            # processed if the display column is being changed
            right_column = bottom_right.column()
            if 2 in range(top_left.column(), bottom_right.column() + 1):
                right_column = self._table_model.columnCount() - 1
            display_item : BaseItem = self._table_model.item(row_idx, 2)
            display = display_item.getValue()
            for col_idx in range(top_left.column(), right_column + 1):
                item : BaseItem = self._table_model.item(row_idx, col_idx)
                if item is None:
                    continue
                if col_idx == 2 and item.getValue() != PropertyDisplay.NONE:
                    # set defaults if needed
                    cleat_item     : BaseItem = self._table_model.item(row_idx, 3)
                    offset_x_item  : BaseItem = self._table_model.item(row_idx, 4)
                    offset_y_item  : BaseItem = self._table_model.item(row_idx, 5)
                    origin_item    : BaseItem = self._table_model.item(row_idx, 6)
                    align_h_item   : BaseItem = self._table_model.item(row_idx, 7)
                    align_v_item   : BaseItem = self._table_model.item(row_idx, 8)
                    width_item     : BaseItem = self._table_model.item(row_idx, 9)
                    height_item    : BaseItem = self._table_model.item(row_idx, 10)
                    color_item     : BaseItem = self._table_model.item(row_idx, 11)
                    family_item    : BaseItem = self._table_model.item(row_idx, 12)
                    size_item      : BaseItem = self._table_model.item(row_idx, 13)
                    bold_item      : BaseItem = self._table_model.item(row_idx, 14)
                    italic_item    : BaseItem = self._table_model.item(row_idx, 15)
                    underline_item : BaseItem = self._table_model.item(row_idx, 16)
                    if cleat_item.getValue() is None:
                        cleat_item.setInitXXX(
                            "" if isinstance(self._item, DrawingScene) \
                            else self._item.__class__.getHandleNames()[0]
                        )
                    if offset_x_item.getValue() is None:
                        offset_x_item.setValue(0.0)
                    if offset_y_item.getValue() is None:
                        offset_y_item.setValue(0.0)
                    if origin_item.getValue() is None:
                        origin_item.setValue(ItemRectHandlesMixin.getHandleNames()[0])
                    if align_h_item.getValue() is None:
                        align_h_item.setValue(AlignH.LEFT)
                    if align_v_item.getValue() is None:
                        align_v_item.setValue(AlignV.TOP)
                    if width_item.getValue() is None:
                        width_item.setValue(None)
                    if height_item.getValue() is None:
                        height_item.setValue(None)
                    if color_item.getValue() is None:
                        color_item.setValue(DEFAULT)
                    if family_item.getValue() is None:
                        family_item.setValue(DEFAULT)
                    if size_item.getValue() is None:
                        size_item.setValue(DEFAULT)
                    if bold_item.getValue() is None:
                        bold_item.setValue(DEFAULT)
                    if italic_item.getValue() is None:
                        italic_item.setValue(DEFAULT)
                    if underline_item.getValue() is None:
                        underline_item.setValue(DEFAULT)
                if col_idx > 2:
                    enabled = (display != PropertyDisplay.NONE)
                    item.setEnabled(enabled)
                    item.setEditable(enabled)
                if item.isEnabled():
                    item.setForeground(QBrush(fg))
                    if item.changed():
                        item.setBackground(QBrush(bg_highlight))
                    else:
                        item.setBackground(QBrush(Qt.GlobalColor.transparent))
                else:
                    item.setForeground(QBrush(Qt.GlobalColor.transparent))
                    item.setBackground(QBrush(Qt.BrushStyle.DiagCrossPattern))

    def _add(self : Self) -> None:
        row_idx = self._table_model.rowCount()
        self._table_model.appendRow([
            NewItem(),                                         # name
            NewItem(),                                         # value
            NewItem(PropertyDisplay.NONE, "PropertyDisplay"),  # display
            NewItem( None , "str"        ),                    # anchor
            NewItem( None , "float"      ),                    # offset X
            NewItem( None , "float"      ),                    # offset Y
            NewItem( None , "str"        ),                    # origin
            NewItem( None , "AlignH"     ),                    # align H
            NewItem( None , "AlignV"     ),                    # align V
            NewItem( None , "float"      ),                    # width
            NewItem( None , "float"      ),                    # height
            NewItem( None , "QColor"     ),                    # color
            NewItem( None , "FontFamily" ),                    # font
            NewItem( None , "FontSize"   ),                    # size
            NewItem( None , "bool"       ),                    # bold
            NewItem( None , "bool"       ),                    # italic
            NewItem( None , "bool"       )                     # underline
        ])
        self._refreshTable()
        self._table_view.setCurrentIndex(self._table_model.index(row_idx, 0))
        self._table_view.edit(self._table_model.index(row_idx, 0))

    def _delete(self : Self) -> None:
        # get all selected rows
        rows = self._selectedRows()
        # delete rows
        failures = []
        for row in rows:
            name_item : BaseItem = self._table_model.item(row, 0)
            if name_item.isEditable():
                before_name = name_item.getBefore()
                if before_name is not None:  # row existed from dialog constructio
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
        max_width = 50  # minimum width
        test_editors = [
            ColorComboBox     (DEFAULT, DEFAULT, None),
            LineWidthComboBox (DEFAULT, DEFAULT, None),
            LineStyleComboBox (DEFAULT, DEFAULT, None),
            FillStyleComboBox (DEFAULT, DEFAULT, None)
        ]
        for editor in test_editors:
            if editor:
                hint = editor.sizeHint()
                max_width = max(max_width, hint.width())
                editor.deleteLater()  # Clean up
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
