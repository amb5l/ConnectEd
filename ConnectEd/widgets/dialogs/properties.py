__all__ = ["PropertiesDialog"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QComboBox, QPushButton, QStyledItemDelegate
from PyQt6.QtGui     import QStandardItemModel, QStandardItem, QBrush

from .table_view import TableView

from ... import hub
from ...core import logger

from ..drawing.items import ElementMixin, KP
from ..drawing.items.property_text import PropertyText, PropertyDisplay

from . import okCancelNewLayout


type PropertiesType = str | float | PropertyDisplay | KP

class PropertiesItem(QStandardItem):
    IDX_INITIAL_TEXT = 0
    IDX_TYPE_NAME = 1
    IDX_INST = 2

    def __init__(
        self: Self,
        value: PropertiesType,
        inst: Optional[Any] = None
    ) -> None:
        if isinstance(value, str):
            text = value
            type_name = "str"
        elif isinstance(value, (int, float)):
            text = str(value)
            type_name = "float"
        elif isinstance(value, PropertyDisplay):
            text = value.value
            type_name = "PropertyDisplay"
        elif isinstance(value, KP):
            text = value.value.name
            type_name = "KP"
        else:
            raise ValueError(f"Invalid value type: {type(value)}")
        super().__init__(text)
        self.setData(text, Qt.ItemDataRole.EditRole)
        self.setData(text, Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)
        self.setData(type_name, Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)
        if inst is not None:
            self.setData(inst, Qt.ItemDataRole.UserRole + self.IDX_INST)

    def textToValue(self: Self, text: str, type_name: str) -> PropertiesType:
        try:
            if type_name == "str":
                return text
            elif type_name == "float":
                return float(text)
            elif type_name == "PropertyDisplay":
                return PropertyDisplay(text)
            elif type_name == "KP":
                enum_key = text.upper().replace(" ", "_")
                if enum_key not in KP.__members__:
                    logger.error(f"Invalid KP enum value: {enum_key}")
                    return self.getInitialValue()
                return KP[enum_key]
            else:
                raise ValueError(f"Invalid type name: {type_name}")
        except Exception as e:
            logger.error(f"Error converting text '{text}' to {type_name}: {e}")
            return self.getInitialValue()

    def getValue(self: Self) -> PropertiesType:
        try:
            text = self.text()
            type_name = self.getTypeName()
            return self.textToValue(text, type_name)
        except Exception as e:
            logger.error(f"Error getting value: {e}")
            return self.text()

    def getInitialValue(self: Self) -> PropertiesType:
        return self.textToValue(self.getInitialText(), self.getTypeName())

    def getInitialText(self: Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)

    def getTypeName(self: Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def getInst(self: Self) -> Optional[Any]:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INST)

    def changed(self: Self) -> bool:
        return self.text() != self.getInitialText()

class PropertiesItemDelegate(QStyledItemDelegate):
    TOOLTIP = None
    ENTRIES = None

    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        if not self.ENTRIES:
            logger.error(f"ENTRIES is None or empty for delegate {self.__class__.__name__}")
            return None
        editor = QComboBox(parent)
        editor.addItems(self.ENTRIES)
        editor.setToolTip(self.TOOLTIP)
        return editor

    def setEditorData(self, editor, index):
        if editor is None:
            logger.error("Editor is None in setEditorData")
            return
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        value_str = str(value) if value is not None else ""
        if value_str in self.ENTRIES:
            editor.setCurrentText(value_str)
        else:
            logger.warning(f"Value '{value_str}' not in ENTRIES, defaulting to {self.ENTRIES[0]}")
            editor.setCurrentText(self.ENTRIES[0])

    def setModelData(self, editor, model, index):
        if editor is None:
            logger.error("Editor is None in setModelData")
            return
        text = editor.currentText()
        model.setData(index, text, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        if editor is not None:
            editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        from PyQt6.QtCore import QSize
        if hasattr(self, 'ENTRIES') and self.ENTRIES:
            from PyQt6.QtGui import QFontMetrics
            font_metrics = QFontMetrics(option.font)
            longest_entry = max(self.ENTRIES, key=len)
            width = font_metrics.horizontalAdvance(longest_entry) + 40
            height = font_metrics.height() + 10
            return QSize(width, height)
        return QSize(100, 25)

class PropertiesDisplayItemDelegate(PropertiesItemDelegate):
    TOOLTIP = "Controls appearance of property"
    ENTRIES = [
        PropertyDisplay.VALUE.value,
        PropertyDisplay.NAME_VALUE.value
    ]

class PropertiesAnchorItemDelegate(PropertiesItemDelegate):
    TOOLTIP = "Controls position of property anchor point"
    ENTRIES = [
        KP.TOP_LEFT.value.name,
        KP.TOP_CENTER.value.name,
        KP.TOP_RIGHT.value.name,
        KP.CENTER_LEFT.value.name,
        KP.CENTER.value.name,
        KP.CENTER_RIGHT.value.name,
        KP.BOTTOM_LEFT.value.name,
        KP.BOTTOM_CENTER.value.name,
        KP.BOTTOM_RIGHT.value.name
    ]

class PropertiesCleatItemDelegate(PropertiesAnchorItemDelegate):
    TOOLTIP = "Controls position of property cleat point"

class PropertiesDialog(QDialog):
    model            : QStandardItemModel
    dialog_layout    : QVBoxLayout
    table_view       : TableView
    ok_cancel_layout : QHBoxLayout
    new_button       : QPushButton
    ok_button        : QPushButton
    cancel_button    : QPushButton
    display_delegate : PropertiesDisplayItemDelegate
    anchor_delegate  : PropertiesAnchorItemDelegate
    cleat_delegate   : PropertiesCleatItemDelegate

    def __init__(self: Self, element: ElementMixin) -> None:
        super().__init__(hub.main_window)
        self.setWindowTitle("Properties")
        self.setModal(True)
        self.dialog_layout = QVBoxLayout(self)
        self.model = QStandardItemModel()
        headers = [label for label in PropertyText.TABLE_ATTRS.keys()]
        self.model.setHorizontalHeaderLabels(headers)
        for p in element.properties:
            row = []
            for label, (_, getter) in PropertyText.TABLE_ATTRS.items():
                value = getter(p)
                item = PropertiesItem(value, p)
                row.append(item)
            self.model.appendRow(row)
        self.table_view = TableView(self.model)
        self.display_delegate = PropertiesDisplayItemDelegate()
        self.anchor_delegate = PropertiesAnchorItemDelegate()
        self.cleat_delegate = PropertiesCleatItemDelegate()
        self.display_delegate.destroyed.connect(
            lambda: self.onDelegateDestroyed("Display")
        )
        self.anchor_delegate.destroyed.connect(
            lambda: self.onDelegateDestroyed("Anchor")
        )
        self.cleat_delegate.destroyed.connect(
            lambda: self.onDelegateDestroyed("Cleat")
        )
        self.table_view.setItemDelegateForColumn(
            list(PropertyText.TABLE_ATTRS.keys()).index("Display"),
            self.display_delegate
        )
        self.table_view.setItemDelegateForColumn(
            list(PropertyText.TABLE_ATTRS.keys()).index("Anchor"),
            self.anchor_delegate
        )
        self.table_view.setItemDelegateForColumn(
            list(PropertyText.TABLE_ATTRS.keys()).index("Cleat"),
            self.cleat_delegate
        )
        self.table_view.resizeColumnsToContents()
        self.dialog_layout.addWidget(self.table_view)
        okCancelNewLayout(self)
        self.setLayout(self.dialog_layout)
        self.adjustSize()
        min_width = self.table_view.horizontalHeader().length() + 50
        min_height = self.table_view.verticalHeader().length() + 50
        self.setMinimumSize(min_width, min_height)
        self.model.dataChanged.connect(self.onDataChanged)

    def onDelegateDestroyed(self, delegate_name: str) -> None:
        """Workaround to fix delegate lifecycle issue (silent crash)."""
        pass

    def onDataChanged(
        self: Self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[int]
    ) -> None:
        if hub.settings.get("display/theme") == "dark":
            bg_highlight = Qt.GlobalColor.darkYellow
        else:
            bg_highlight = Qt.GlobalColor.yellow
        for row in range(top_left.row(), bottom_right.row() + 1):
            for col in range(top_left.column(), bottom_right.column() + 1):
                item = self.model.item(row, col)
                if item and item.getInitialText() != item.text():
                    item.setBackground(QBrush(bg_highlight))
                else:
                    item.setBackground(QBrush(Qt.GlobalColor.transparent))

    def new(self: Self) -> None:
        row = self.model.rowCount()
        self.model.appendRow([
            PropertiesItem(""),
            PropertiesItem(""),
            PropertiesItem(PropertyDisplay.VALUE),
            PropertiesItem(KP.TOP_LEFT),
            PropertiesItem(0),
            PropertiesItem(0),
            PropertiesItem(KP.BOTTOM_RIGHT)
        ])
        self.table_view.setCurrentIndex(self.model.index(row, 0))

    def getChanges(self: Self) -> dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]:
        r = {}
        for row_num in range(self.model.rowCount()):
            item_name: PropertiesItem = self.model.item(row_num, 0)
            key: PropertyText = item_name.getInst()
            r[key] = []
            for col in range(self.model.columnCount()):
                item: PropertiesItem = self.model.item(row_num, col)
                if item.changed():
                    label = self.model.horizontalHeaderItem(col).text()
                    before = item.getInitialValue()
                    after = item.getValue()
                    r[key].append((label, before, after))
        return r
