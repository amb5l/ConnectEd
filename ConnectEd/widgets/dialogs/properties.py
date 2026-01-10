from typing import Self, Any, TypeAlias
from enum   import Enum
from copy   import deepcopy

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView
from PyQt6.QtGui     import QBrush

from ...app import settings

from ..graphics.property import PropertyState,         \
                                PropertyEdit,          \
                                PropertyTextLineState, \
                                PropertyTextBlockState

from ..graphics.items import DEFAULT

from ..graphics.items.property_text import PropertyTextLine, PropertyTextBlock

from ..graphics.items.mixin.handle import ItemRectHandlesMixin

from .components.model import DialogItem, DialogModel

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


class DisplayChoice(Enum):
    NONE         = "<none>"
    LINE         = "Line"
    BLOCK        = "Block"


class ExistingItem(DialogItem):
    def __init__(
        self     : Self,
        value    : Any,
        kind     : str = "str",
        default  : Any = None,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__(value, value, kind, default, editable, enabled)


class NewItem(DialogItem):
    def __init__(
        self     : Self,
        value    : Any = "",
        kind     : str = "str",
        default  : Any = None,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__(None, value, kind, default, editable, enabled)


class PropertiesDialog(QDialog):
    ItemType : TypeAlias = "PropertiesMixin"

    _item           : ItemType
    _dialog_layout  : QVBoxLayout
    _table_model    : DialogModel
    _table_view     : TableView
    _delegate       : DialogItemDelegate
    _button_layout  : QHBoxLayout
    _display_button : QPushButton
    _add_button     : QPushButton
    _delete_button  : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton
    _before         : dict[str, PropertyState]
    _current        : dict[str, PropertyState]

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
        # build model, record before state
        self._table_model = DialogModel()
        headers = [
            "Name",
            "Value",
            "Display",
            "Hidden",
            "Tether",
            "Offset X",
            "Offset Y",
            "Anchor",
            "Color",
            "Font",
            "Size",
            "Bold",
            "Italic",
            "Underline",
            "Align H",
            "Align V",
            "Width",
            "Height"
        ]
        self._table_model.setHorizontalHeaderLabels(headers)
        self._before = {}
        for name, prop in item.properties.items():
            pt = prop.getText()
            if isinstance(pt, PropertyTextLine):
                pt_state_class = PropertyTextLineState
                display_choice = DisplayChoice.LINE
            elif isinstance(pt, PropertyTextBlock):
                pt_state_class = PropertyTextBlockState
                display_choice = DisplayChoice.BLOCK
            else:
                display_choice = DisplayChoice.NONE
            args = {}
            if display_choice is not None:
                args[ "hidden"    ] = not pt.isVisible(),
                args[ "cleat"     ] = pt.getCleat(),
                args[ "offset_x"  ] = pt.pos().x(),
                args[ "offset_y"  ] = pt.pos().y(),
                args[ "origin"    ] = pt.getOrigin(),
                args[ "color"     ] = pt.quillColor(),
                args[ "font"      ] = pt.quillFamily(),
                args[ "size"      ] = pt.quillSize(),
                args[ "bold"      ] = pt.quillBold(),
                args[ "italic"    ] = pt.quillItalic(),
                args[ "underline" ] = pt.quillUnderline()
            if pt_state_class == PropertyTextBlockState:
                args["align_h"    ] = pt.alignH()
                args["align_v"    ] = pt.alignV()
                args["width"      ] = pt.width()
                args["height"     ] = pt.height()
            pt_state = pt_state_class(**args) if args else None
            state = PropertyState(name, prop.raw(), pt_state)
            inherent  = prop.inherent()
            read_only = prop.isReadOnly()
            kind      = prop.kind()
            default   = prop.default()
            display_hidden    = None
            display_cleat     = None
            display_offset_x  = None
            display_offset_y  = None
            display_origin    = None
            display_color     = None
            display_font      = None
            display_size      = None
            display_bold      = None
            display_italic    = None
            display_underline = None
            display_align_h   = None
            display_align_v   = None
            display_width     = None
            display_height    = None
            if display_choice is not DisplayChoice.NONE:
                display_hidden    = pt_state.hidden
                display_cleat     = pt_state.cleat
                display_offset_x  = pt_state.offset_x
                display_offset_y  = pt_state.offset_y
                display_origin    = pt_state.origin
                display_color     = pt_state.color
                display_font      = pt_state.font
                display_size      = pt_state.size
                display_bold      = pt_state.bold
                display_italic    = pt_state.italic
                display_underline = pt_state.underline
            if display_choice is DisplayChoice.BLOCK:
                display_align_h   = pt_state.align_h
                display_align_v   = pt_state.align_v
                display_width     = pt_state.width
                display_height    = pt_state.height
            self._table_model.appendRow([
                ExistingItem(state.name, editable=inherent),
                ExistingItem(state.value, kind, default, not read_only),
                ExistingItem(display_choice    , "DisplayChoice"),
                ExistingItem(display_hidden    , "bool"         ),
                ExistingItem(display_cleat     , "str"          ),
                ExistingItem(display_offset_x  , "float"        ),
                ExistingItem(display_offset_y  , "float"        ),
                ExistingItem(display_origin    , "str"          ),
                ExistingItem(display_color     , "QColor"       ),
                ExistingItem(display_font      , "FontFamily"   ),
                ExistingItem(display_size      , "FontSize"     ),
                ExistingItem(display_bold      , "bool"         ),
                ExistingItem(display_italic    , "bool"         ),
                ExistingItem(display_underline , "bool"         ),
                ExistingItem(display_align_h   , "AlignH"       ),
                ExistingItem(display_align_v   , "AlignV"       ),
                ExistingItem(display_width     , "float"        ),
                ExistingItem(display_height    , "float"        )
            ])
            self._before[name] = state
        # initially, current = before
        self._current = deepcopy(self._before)
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

    def parent(self : Self) -> "DrawingView | None":
        return super().parent()

    def getColumn(self : Self, header : str) -> int:
        return self._HEADER.index(header)

    def getChanges(self : Self) -> dict[str, PropertyEdit]:
        before_after : dict[str, PropertyEdit] = {}
        name_rows : dict[str, int] = {}
        # check for and ignore duplicates
        for row_idx in range(self._table_model.rowCount()):
            name_item : DialogItem = self._table_model.item(row_idx, 0)
            after_name = name_item.getValue()
            if after_name in name_rows:
                QMessageBox.warning(
                    self,
                    "Property Name Duplicated",
                    f"Property '{after_name}' appears multiple times"
                )
                continue  # skip duplicate
            before_name = name_item.getBefore()
            if before_name is not None:  # existing property
                if before_name not in self._before.keys():
                    QMessageBox.warning(
                        self,
                        "Anomalous Property",
                        f"Property '{before_name}' not seen during construction"
                    )
                    continue  # skip anomalous property
                before = self._before[before_name]
            else:
                before = None
            value_item     : DialogItem = self._table_model.item(row_idx, 1)
            display_item   : DialogItem = self._table_model.item(row_idx, 2)
            hidden_item    : DialogItem = self._table_model.item(row_idx, 3)
            cleat_item     : DialogItem = self._table_model.item(row_idx, 4)
            offset_x_item  : DialogItem = self._table_model.item(row_idx, 5)
            offset_y_item  : DialogItem = self._table_model.item(row_idx, 6)
            origin_item    : DialogItem = self._table_model.item(row_idx, 7)
            color_item     : DialogItem = self._table_model.item(row_idx, 8)
            font_item      : DialogItem = self._table_model.item(row_idx, 9)
            size_item      : DialogItem = self._table_model.item(row_idx, 10)
            bold_item      : DialogItem = self._table_model.item(row_idx, 11)
            italic_item    : DialogItem = self._table_model.item(row_idx, 12)
            underline_item : DialogItem = self._table_model.item(row_idx, 13)
            align_h_item   : DialogItem = self._table_model.item(row_idx, 14)
            align_v_item   : DialogItem = self._table_model.item(row_idx, 15)
            width_item     : DialogItem = self._table_model.item(row_idx, 16)
            height_item    : DialogItem = self._table_model.item(row_idx, 17)
            after = PropertyState()
            after = PropertyState(
                name      = after_name,
                value     = value_item.getValue(),
                display   = display_item.getValue()
            )
            if after.display != DisplayChoice.NONE:
                after.hidden    = hidden_item.getValue()
                after.cleat     = cleat_item.getValue()
                after.offset_x  = offset_x_item.getValue()
                after.offset_y  = offset_y_item.getValue()
                after.origin    = origin_item.getValue()
                after.color     = color_item.getValue()
                after.font      = font_item.getValue()
                after.size      = size_item.getValue()
                after.bold      = bold_item.getValue()
                after.italic    = italic_item.getValue()
                after.underline = underline_item.getValue()
            key = after_name if before_name is None else before_name
            before_after[key] = PropertyEdit(before, after)
        changes : dict[str, PropertyEdit] = {}
        for change in before_after.values():
            if change.before != change.after:
                name = change.after.name if change.before is None \
                    else change.before.name
                changes[name] = change
        return changes

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
            display_item : DialogItem = self._table_model.item(row_idx, 2)
            display = display_item.getValue()
            for col_idx in range(top_left.column(), right_column + 1):
                item : DialogItem = self._table_model.item(row_idx, col_idx)
                if item is None:
                    continue
                if col_idx == 2 and item.getValue() != DisplayChoice.NONE:
                    # set defaults if needed
                    cleat_item     : DialogItem = self._table_model.item(row_idx, 3)
                    offset_x_item  : DialogItem = self._table_model.item(row_idx, 4)
                    offset_y_item  : DialogItem = self._table_model.item(row_idx, 5)
                    origin_item    : DialogItem = self._table_model.item(row_idx, 6)
                    color_item     : DialogItem = self._table_model.item(row_idx, 7)
                    font_item      : DialogItem = self._table_model.item(row_idx, 8)
                    size_item      : DialogItem = self._table_model.item(row_idx, 9)
                    bold_item      : DialogItem = self._table_model.item(row_idx, 10)
                    italic_item    : DialogItem = self._table_model.item(row_idx, 11)
                    underline_item : DialogItem = self._table_model.item(row_idx, 12)
                    if cleat_item.getValue() is None:
                        cleat_item.setInit(
                            "" if isinstance(self._item, DrawingScene) \
                            else self._item.__class__.getHandleNames()[0]
                        )
                    if offset_x_item.getValue() is None:
                        offset_x_item.setInit(0.0)
                    if offset_y_item.getValue() is None:
                        offset_y_item.setInit(0.0)
                    if origin_item.getValue() is None:
                        origin_item.setInit(ItemRectHandlesMixin.getHandleNames()[0])
                    if color_item.getValue() is None:
                        color_item.setInit(DEFAULT)
                    if font_item.getValue() is None:
                        font_item.setInit(DEFAULT)
                    if size_item.getValue() is None:
                        size_item.setInit(DEFAULT)
                    if bold_item.getValue() is None:
                        bold_item.setInit(DEFAULT)
                    if italic_item.getValue() is None:
                        italic_item.setInit(DEFAULT)
                    if underline_item.getValue() is None:
                        underline_item.setInit(DEFAULT)
                if col_idx > 2:
                    enabled = (display != DisplayChoice.NONE)
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
            NewItem(),                                     # name
            NewItem(),                                     # value
            NewItem(DisplayChoice.NONE, "DisplayChoice"),  # display
            NewItem( False , "bool"       ),                # hidden
            NewItem( None , "str"        ),                # anchor
            NewItem( None , "float"      ),                # offset X
            NewItem( None , "float"      ),                # offset Y
            NewItem( None , "str"        ),                # origin
            NewItem( None , "QColor"     ),                # color
            NewItem( None , "FontFamily" ),                # font
            NewItem( None , "FontSize"   ),                # size
            NewItem( None , "bool"       ),                # bold
            NewItem( None , "bool"       ),                # italic
            NewItem( None , "bool"       )                 # underline
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
            name_item : DialogItem = self._table_model.item(row, 0)
            if name_item.isEditable():
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
            ColorComboBox     (DEFAULT, DEFAULT, DEFAULT, None),
            LineWidthComboBox (DEFAULT, DEFAULT, DEFAULT, None),
            LineStyleComboBox (DEFAULT, DEFAULT, DEFAULT, None),
            FillStyleComboBox (DEFAULT, DEFAULT, DEFAULT, None)
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
