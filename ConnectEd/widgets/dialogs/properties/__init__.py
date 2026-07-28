from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore    import Qt, QModelIndex, QItemSelectionModel
from PyQt6.QtWidgets import QDialog, QMessageBox, \
                            QVBoxLayout, QHBoxLayout, QPushButton, \
                            QAbstractItemView
from PyQt6.QtGui     import QStandardItemModel, QColor, QFontDatabase

from ....app import logger

from ....core.check import checked
from ....core.types import (
    NoChange, NO_CHANGE, AlignH, AlignV, HandleId, Display, DataKind,
    RectHandleId, LineHandleId, BlockPinHandleId, SymbolPinHandleId,
)

from ...graphics.properties import PropertiesMixin

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
    from ...graphics.views.diagram import DiagramView


_PT_COLS = {
#                   kind                   default value              method name
    "Cleat"     : ( None                 , None                     , "cleat"         ), # noqa E501
    "X"         : ( DataKind.FLOAT       , 0.0                      , "x"             ), # noqa E501
    "Y"         : ( DataKind.FLOAT       , 0.0                      , "y"             ), # noqa E501
    "Rotation"  : ( DataKind.ROTATION    , 0.0                      , "rotation"      ), # noqa E501
    "Mirror H"  : ( DataKind.BOOL        , False                    , "mirrorH"       ), # noqa E501
    "Mirror V"  : ( DataKind.BOOL        , False                    , "mirrorV"       ), # noqa E501
    "Auto Flip" : ( DataKind.BOOL        , True                     , "autoflip"      ), # noqa E501
    "Origin"    : ( DataKind.RECT_HANDLE , RectHandleId.BOTTOM_LEFT , "origin"        ), # noqa E501
    "Align H"   : ( DataKind.ALIGN_H     , AlignH.LEFT              , "alignH"        ), # noqa E501
    "Align V"   : ( DataKind.ALIGN_V     , AlignV.TOP               , "alignV"        ), # noqa E501
    "Width"     : ( DataKind.SIZE        , None                     , "width"         ), # noqa E501
    "Height"    : ( DataKind.SIZE        , None                     , "height"        ), # noqa E501
    "Color"     : ( DataKind.COLOR       , None                     , "textColor"     ), # noqa E501
    "Font"      : ( DataKind.FONT_FAMILY , None                     , "textFont"      ), # noqa E501
    "Size"      : ( DataKind.FONT_SIZE   , None                     , "textSize"      ), # noqa E501
    "Bold"      : ( DataKind.FONT_BOOL   , None                     , "textBold"      ), # noqa E501
    "Italic"    : ( DataKind.FONT_BOOL   , None                     , "textItalic"    ), # noqa E501
    "Underline" : ( DataKind.FONT_BOOL   , None                     , "textUnderline" )  # noqa E501
}


_COLS : list[str] = ["Name", "Type", "Value", "Display"] + list(_PT_COLS.keys())


_HANDLE_KIND : dict[type, DataKind] = {
    RectHandleId      : DataKind.RECT_HANDLE,
    LineHandleId      : DataKind.LINE_HANDLE,
    BlockPinHandleId  : DataKind.BLOCK_PIN_HANDLE,
    SymbolPinHandleId : DataKind.SYMBOL_PIN_HANDLE
}


class PropertiesDialog(QDialog):
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

    @checked
    def __init__(
        self : Self,
        item : PropertiesMixin,
        view : DiagramView | None = None
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
            if (kind := item.properties.kind(name)) is None:
                continue
            self._table_model.appendRow(self._buildRow(
                name, kind, item.properties.value(name)
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
        horizontal_header = self._table_view.horizontalHeader()
        vertical_header = self._table_view.verticalHeader()
        if horizontal_header is not None and vertical_header is not None:
            min_width = horizontal_header.length() + 50
            min_height = vertical_header.length() + 50
            self.setMinimumSize(min_width, min_height)
        self._table_model.dataChanged.connect(self._onDataChanged)

    def accept(self : Self) -> None:
        name_col = _COLS.index("Name")
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
            # check for type/value mismatches on new properties
            if (kind_item := self._getItem(row, kind_col)) is None:
                logger().error(f"Bad kind item for row {row}")
                continue
            if not kind_item.isEditable():
                continue
            if not isinstance(kind := kind_item.value(), DataKind):
                logger().error(f"Kind is not a DataKind: {kind}")
                return
            if (value_item := self._getItem(row, value_col)) is None:
                logger().error(f"Bad value item for row {row}")
                continue
            if kind != value_item.kind():
                logger().warning(f"Type/value mismatch for property '{name}'")
                value_item.setKind(kind)
            if not isinstance(value := value_item.value(), kind.types()):
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
        model = self._table_model
        changes : list[PropertyChangeType] = []
        # deletions
        for row_idx in range(model.rowCount()):
            if (name_item := self._getItem(row_idx, 0)) is None:
                logger().error(f"Bad name item for row {row_idx}")
                continue
            if name_item.deleted():
                name = name_item.value()
                if not isinstance(name, str):
                    logger().error(f"Name is not a string: {name}")
                    continue
                changes.append(PropertyChangeDelete(name))
        # additions and modifications
        for row_idx in range(model.rowCount()):
            if (name_item := self._getItem(row_idx, _COLS.index("Name"))) is None:
                logger().error(f"Bad name item for row {row_idx}")
                continue
            if not isinstance(name := name_item.value(), str):
                logger().error(f"Name is not a string: {name}")
                continue
            if (kind_item := self._getItem(row_idx, _COLS.index("Type"))) is None:
                logger().error(f"Bad kind item for row {row_idx}")
                continue
            if not isinstance(kind := kind_item.value(), DataKind):
                logger().error(f"Kind is not a DataKind: {kind}")
                continue
            if (value_item := self._getItem(row_idx, _COLS.index("Value"))) is None:
                logger().error(f"Bad value item for row {row_idx}")
                continue
            value = value_item.value()
            if (display_item := self._getItem(row_idx, _COLS.index("Display"))) is None:
                logger().error(f"Bad display item for row {row_idx}")
                continue
            display = display_item.value()
            if name_item.new():
                # addition
                changes.append(PropertyChangeAdd(name, kind, value))
                # property text
                if display != Display.NONE:
                    pt_args = self._getRowPropertyTextItemValues(row_idx)
                    if pt_args is not None:
                        changes.append(PropertyChangeTextAdd(
                            name,
                            display == Display.SHOW,
                            *pt_args
                        ))
            else:
                # modification
                if name_item.changed() \
                or kind_item.changed() \
                or value_item.changed():
                    changes.append(PropertyChangeModify(name, kind, value))
                # property text modification
                if display_item.changed():
                    if display == Display.NONE:
                        changes.append(PropertyChangeTextDelete(name))
                    elif display_item.initial() == Display.NONE:
                        pt_args = self._getRowPropertyTextItemValues(row_idx)
                        if pt_args is not None:
                            changes.append(PropertyChangeTextAdd(
                                name, display == Display.SHOW, *pt_args
                            ))
                    else:
                        pt_args = self._getRowPropertyTextItemValueDeltas(row_idx)
                        if pt_args is not None:
                            changes.append(PropertyChangeTextModify(
                                name, display == Display.SHOW, *pt_args
                            ))
        return changes

    def _getItem(
        self    : Self,
        row_idx : int,
        col_idx : int
    ) -> PropertiesItem | None:
        item = self._table_model.item(row_idx, col_idx)
        return None if not isinstance(item, PropertiesItem) else item

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
        display : Display,
        row_idx : int
    ) -> None:
        item = self._item
        pt_new = False
        for col_name, (kind, value, _) in _PT_COLS.items():
            col_idx = _COLS.index(col_name)
            if (pt_item := self._getItem(row_idx, col_idx)) is None:
                logger().error(f"Bad PT item for row {row_idx}")
                continue
            if pt_item is not None and col_name == "Cleat":
                pt_new = pt_item.new()
            if display != Display.NONE and pt_item is None:
                if not isinstance(item, ItemHandlesMixin):
                    raise TypeError("Bad item")
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
        if not isinstance(display_item := self._table_model.item(row_idx, display_col), PropertiesItem):
            logger().error(f"Bad display item for row {row_idx}")
            return
        if not isinstance(display_value := display_item.value(), Display):
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

    def _buildRow(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> list[PropertiesItem | None]:
        item = self._item
        new = not item.properties.has(name)
        custom = new or not item.properties.inherent(name)
        if not isinstance(value_kind := kind if new else item.properties.kind(name), DataKind):
            logger().error(f"Bad value kind ({value_kind})")
            value_kind = DataKind.STR
        value_value = value if new else item.properties.value(name)
        value_default = None if new else item.properties.default(name)
        value_editable = item.properties.writeable(name) is True
        pt = None if new else item.properties.text(name)
        display = \
            Display.NONE if pt is None else \
            Display.SHOW if pt.isVisible() else \
            Display.HIDE
        row : list[PropertiesItem | None] = [
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
                kind     = value_kind,
                value    = value_value,
                default  = value_default,
                new      = new,
                editable = value_editable
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
            if (name_item := self._getItem(row, 0)) is None:
                logger().error(f"Bad name item for row {row}")
                continue
            if not isinstance(name := name_item.value(), str):
                logger().error(f"Name is not a string: {name}")
                continue
            if not self._item.properties.has(name) \
            or not self._item.properties.inherent(name):
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
