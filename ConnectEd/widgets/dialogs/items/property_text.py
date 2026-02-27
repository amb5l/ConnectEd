from typing import Self

from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel

from .text import TextItemDialogMixin


class PropertyTextItemDialog(TextItemDialogMixin, QDialog):
    _property_layout : QGridLayout
    _name_label      : QLabel


    @checked
    def getText(self : Self) -> str:
        raise NotImplementedError("PropertyTextItemDialog.getText() is not implemented")

    @checked
    def getName(self : Self) -> str:
        return self._name_input.text()

    def _mainSection(self : Self) -> None:
        self._value_layout = QGridLayout()
