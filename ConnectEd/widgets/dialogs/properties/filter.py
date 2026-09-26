from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout

from ...graphics.properties        import PropertiesMixin

from ..components.check_list       import CheckList

from ..components.layout.ok_cancel import OkCancelLayout


class PropertyNamesFilterDialog(QDialog):
    _items            : list[PropertiesMixin]
    _check_list       : CheckList
    _layout           : QVBoxLayout
    _ok_cancel_layout : OkCancelLayout

    def __init__(
        self   : Self,
        items  : list[PropertiesMixin],
        parent : QWidget | None = None
    ) -> None:
        # superclass init
        super().__init__(parent)
        self.setWindowTitle("Property NamesFilter")
        self.setModal(True)
        self._items = items
        self._ok_cancel_layout = OkCancelLayout(self)
        ok_button = self._ok_cancel_layout._ok_button
        property_names = [
            property_name
            for item in items
            for property_name in item.properties.keys()
        ]
        self._check_list = CheckList(property_names, ok_button)
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._check_list)
        self._layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._layout)

