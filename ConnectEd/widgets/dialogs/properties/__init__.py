from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout

from ...graphics.properties import PropertiesMixin

from ...graphics.items.mixin import ItemMixin

from ..components.layout.ok_cancel import OkCancelLayout

from .item_type import (
    PropertiesItemTypeWidget, PropertiesItemTypeTabWidget
)


class PropertiesDialog(QDialog):
    """
    Dialog for editing properties.
    """

    _main_widget : PropertiesItemTypeWidget | PropertiesItemTypeTabWidget

    def __init__(
        self   : Self,
        items  : list[PropertiesMixin],
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # process items
        if len(items) == 0:
            raise ValueError("No items")
        items_dict : dict[str, list[PropertiesMixin]] = {}
        for item in items:
            if not isinstance(item, ItemMixin):
                raise ValueError(f"Item {item} is not a ItemMixin")
            item_type = item.description()
            items_dict.setdefault(item_type, []).append(item)
        # set window title
        item_types = list(items_dict.keys())
        if len(items) == 1:
            title = f"{item_types[0]} Properties"
        elif len(item_types) == 1:
            title = f"{item_types[0]} Properties ({len(items)} items)"
        else:
            title = f"Properties ({len(items)} items)"
        self.setWindowTitle(title)
        # create main widget
        if len(items_dict.keys()) == 1:
            self._main_widget = PropertiesItemTypeWidget(items)
        else:
            self._main_widget = PropertiesItemTypeTabWidget()
            for item_type in items_dict.keys():
                self._main_widget.addTab(
                    PropertiesItemTypeWidget(items_dict[item_type]),
                    item_type
                )
        # buttons
        ok_cancel_layout = OkCancelLayout(self)
        # create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._main_widget)
        layout.addLayout(ok_cancel_layout)
        self.setLayout(layout)
