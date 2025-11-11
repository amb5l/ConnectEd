from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QPushButton, QAbstractItemView
from PyQt6.QtGui     import QColor

from ..graphics.properties import PropertiesMixin

from ..graphics.items.property_text import PropertyDisplay

from .components.model      import DialogItem, DialogModel
from .components.delegate   import DialogItemDelegate
from .components.table_view import TableView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.views.drawing import DrawingView


@dataclass
class PropertyDisplayState:
    display   : PropertyDisplay
    handle    : str
    offset_x  : float
    offset_y  : float
    origin    : str
    color     : QColor
    font      : str
    size      : float
    bold      : bool
    italic    : bool
    underline : bool


@dataclass
class PropertyDisplayChange:
    before : PropertyDisplayState | None
    after  : PropertyDisplayState | None


class PropertiesDisplayDialog(QDialog):
    _dialog_layout  : QVBoxLayout
    _table_model    : DialogModel
    _table_view     : TableView
    _value_delegate : DialogItemDelegate
    _button_layout  : QHBoxLayout
    _display_button : QPushButton
    _add_button     : QPushButton
    _delete_button  : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton
    _initial        : dict[str, Any]

    def __init__(
        self : Self,
        item : PropertiesMixin,
        view : "DrawingView | None" = None
    ) -> None:
        # initialise
        super().__init__(view)
        self.setWindowTitle(f"{item.__class__.__name__} Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # build model
        self._initial = {}
        self._table_model = DialogModel()
        headers = [snake2proper(field.name) for field in fields(PropertyState)]
        self._table_model.setHorizontalHeaderLabels(["Name", "Value"])

        header = [
            "Name",      # Property - Name
            "Value",     # Property - Value
            "Display",   # DisplayChoice
            "Handle",    # PropertyText - Handle
            "Offset X",  # PropertyText - Offset
            "Offset Y",  # PropertyText - Offset
            "Origin",    # PropertyText - Origin
            "Color",     # PropertyText.a.text - Color
            "Font",      # PropertyText.a.text - Font
            "Size",      # PropertyText.a.text - Size
            "Bold",      # PropertyText.a.text - Bold
            "Italic",    # PropertyText.a.text - Italic
            "Underline"  # PropertyText.a.text - Underline
        ]
        self._table_model.setHorizontalHeaderLabels(header)
        for name, property_text in item.getPropertyTexts().items():
            value = item.getPropertyValue(name)
            display = property_text.display()
            cleat = property_text.getCleat()
            offset_x = property_text.pos().x()
            offset_y = property_text.pos().y()
            origin = property_text.getOrigin()
            color = property_text.a.quill.getColor()
            font = property_text.a.quill.getFamily()
            size = property_text.a.quill.getSize()
            bold = property_text.a.quill.getBold()
            italic = property_text.a.quill.getItalic()
            underline = property_text.a.quill.getUnderline()
            row = [
                DialogItem( name      , "str"             , editable=False ),
                DialogItem( value     , "str"             , editable=False ),
                DialogItem( display   , "PropertyDisplay" , editable=True  ),
                DialogItem( cleat     , "str"             , editable=True  ),
                DialogItem( offset_x  , "float"           , editable=True  ),
                DialogItem( offset_y  , "float"           , editable=True  ),
                DialogItem( origin    , "str"             , editable=True  ),
                DialogItem( color     , "QColor"          , editable=True  ),
                DialogItem( font      , "str"             , editable=True  ),
                DialogItem( size      , "float"           , editable=True  ),
                DialogItem( bold      , "bool"            , editable=True  ),
                DialogItem( italic    , "bool"            , editable=True  ),
                DialogItem( underline , "bool"            , editable=True  )
            ]
            self._table_model.appendRow(row)
            self._initial[name] = value
        # create delegate
        self._value_delegate = DialogItemDelegate()
        self._value_delegate.destroyed.connect(
            lambda: self._onDelegateDestroyed("Value")
        )
        # build table view
        self._table_view = TableView(self._table_model)
        for col in range(2, len(header)):
            self._table_view.setItemDelegateForColumn(col, self._value_delegate)
        self._table_view.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self._table_view.resizeColumnsToContents()
        self._table_view.setColumnWidth(1, self._getValueColumnWidth())
        # build button layout
        self._button_layout = QHBoxLayout()
        self._display_button = QPushButton("Display")
        self._display_button.clicked.connect(self._display)
        self._button_layout.addWidget(self._display_button)
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

    def getStates(self) -> dict[str, PropertyDisplayState]:
        states = {}  # return value
        for row in range(self._table_model.rowCount()):
            name_item : DialogItem = self._table_model.item(row, 0)
            display_item : DialogItem = self._table_model.item(row, 2)
            cleat_item : DialogItem = self._table_model.item(row, 3)
            offset_x_item : DialogItem = self._table_model.item(row, 4)
            offset_y_item : DialogItem = self._table_model.item(row, 5)
            origin_item : DialogItem = self._table_model.item(row, 6)
            color_item : DialogItem = self._table_model.item(row, 7)
            font_item : DialogItem = self._table_model.item(row, 8)
            size_item : DialogItem = self._table_model.item(row, 9)
            bold_item : DialogItem = self._table_model.item(row, 10)
            italic_item : DialogItem = self._table_model.item(row, 11)
            underline_item : DialogItem = self._table_model.item(row, 12)
            states[name_item.getValue()] = PropertyDisplayState(
                display_item.getValue(),
                cleat_item.getValue(),
                offset_x_item.getValue(),
                offset_y_item.getValue(),
                origin_item.getValue(),
                color_item.getValue(),
                font_item.getValue(),
                size_item.getValue(),
                bold_item.getValue(),
                italic_item.getValue(),
                underline_item.getValue()
            )
        return states

    def _onDelegateDestroyed(self : Self, _ : str) -> None:
        """Workaround to fix delegate lifecycle issue (silent crash)."""
        pass

    def _add(self):
        pass
