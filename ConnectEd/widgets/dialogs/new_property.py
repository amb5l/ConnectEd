from typing import Self, TypeAlias, Any

from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel

from ...core.types import DataKind

from .components.edit import StrEditor, TextEditor, \
                             IntEditor, FloatEditor, BoolEditor

from .components.combo.enum        import EnumComboBox

from .components.layout.ok_cancel import OkCancelLayout


EditorType : TypeAlias = \
    StrEditor          | \
    TextEditor         | \
    IntEditor          | \
    FloatEditor        | \
    BoolEditor


class NewPropertyDialog(QDialog):
    _dialog_layout    : QVBoxLayout
    _name_label       : QLabel
    _name_edit        : StrEditor
    _kind_label       : QLabel
    _kind_combo       : EnumComboBox[DataKind]
    _value_layout     : QHBoxLayout | QVBoxLayout
    _value_layout_idx : int
    _value_label      : QLabel
    _value_edit       : EditorType
    _ok_cancel_layout : OkCancelLayout

    def __init__(self : Self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Property")
        self.setModal(True)
        # name
        self._name_label = QLabel("Name:")
        self._dialog_layout.addWidget(self._name_label)
        self._name_edit = StrEditor()
        self._dialog_layout.addWidget(self._name_edit)
        # kind
        self._kind_label = QLabel("Kind:")
        self._dialog_layout.addWidget(self._kind_label)
        editors = EditorType.__args__
        self._kind_combo = EnumComboBox[DataKind](DataKind.STR, tuple(editors))
        self._dialog_layout.addWidget(self._kind_combo)
        # value
        self._value_layout_idx = self._dialog_layout.count()
        self._onKindChanged()
        # finalise
        self._kind_combo.currentIndexChanged.connect(self._onKindChanged)
        self._onKindChanged()

    def _onKindChanged(self : Self, index : int) -> None:
        """Change editor widget based on selected kind."""
        # remove current layout if it exists
        if hasattr(self, '_value_layout'):
            self._value_layout.deleteLater()
            self._dialog_layout.removeItem(self._value_layout)
        # create new widget based on selected kind
        kind = self._kind_combo.value()
        editor = kind.editor
        self._value_layout = QVBoxLayout() if kind == DataKind.TEXT else QHBoxLayout()
        self._dialog_layout.insertLayout(self._value_layout_idx, self._value_layout)
        self._value_label = QLabel("Value:")
        self._value_layout.addWidget(self._value_label)
        self._value_layout.addWidget(editor)

    def getName(self : Self) -> str:
        return self._name_edit.text()

    def getKind(self : Self) -> DataKind:
        return self._kind_combo.value()

    def getValue(self : Self) -> Any:
        return self._value_edit.value()
