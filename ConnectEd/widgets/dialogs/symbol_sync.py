from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QCheckBox

from ...core.check import checked

from ..graphics.items.symbol import SymbolInstanceItem

from .components.layout.ok_cancel import OkCancelLayout

class SymbolSyncDialog(QDialog):
    """
    Dialog to support partial or full synchronization of a symbol instance with
    its definition.
    """

    _dialog_layout        : QVBoxLayout
    _checkbox_layout      : QVBoxLayout
    _inherent_checkbox    : QCheckBox
    _custom_checkbox      : QCheckBox
    _text_add_checkbox    : QCheckBox
    _text_remove_checkbox : QCheckBox
    _text_reset_checkbox  : QCheckBox
    _ok_cancel_layout     : OkCancelLayout

    @checked
    def __init__(
        self    : Self,
        symbols : SymbolInstanceItem | list[SymbolInstanceItem],
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if isinstance(symbols, SymbolInstanceItem):
            symbols = [symbols]
        n = len(symbols)
        if n == 1:
            self.setWindowTitle(f"Synchronize Symbol {symbols[0].name()}")
        else:
            self.setWindowTitle(f"Synchronize {n} Symbols")
        self._dialog_layout = QVBoxLayout(self)
        self._checkbox_layout = QVBoxLayout()
        self._inherent_checkbox = QCheckBox(
            "Copy inherent property values from definition"
        )
        self._checkbox_layout.addWidget(self._inherent_checkbox)
        self._custom_checkbox = QCheckBox(
            "Remove custom properties and their texts"
        )
        self._checkbox_layout.addWidget(self._custom_checkbox)
        self._text_add_checkbox = QCheckBox(
            "Add definition property texts missing from instance"
        )
        self._checkbox_layout.addWidget(self._text_add_checkbox)
        self._text_remove_checkbox = QCheckBox(
            "Remove instance property texts not in definition"
        )
        self._checkbox_layout.addWidget(self._text_remove_checkbox)
        self._text_reset_checkbox = QCheckBox(
            "Reset instance property text positions to match definition"
        )
        self._checkbox_layout.addWidget(self._text_reset_checkbox)
        self._dialog_layout.addLayout(self._checkbox_layout)
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._dialog_layout)

    @checked
    def inherent(self : Self) -> bool:
        return self._inherent_checkbox.isChecked()

    @checked
    def custom(self : Self) -> bool:
        return self._custom_checkbox.isChecked()

    @checked
    def text_add(self : Self) -> bool:
        return self._text_add_checkbox.isChecked()

    @checked
    def text_remove(self : Self) -> bool:
        return self._text_remove_checkbox.isChecked()

    @checked
    def text_reset(self : Self) -> bool:
        return self._text_reset_checkbox.isChecked()
