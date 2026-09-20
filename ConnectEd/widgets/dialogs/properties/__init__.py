from __future__ import annotations

from typing      import Self
from dataclasses import dataclass, replace

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QGraphicsItem

from ...graphics.properties import Property, PropertyState, PropertiesMixin

from ...graphics.items.property_text import PropertyTextItem, PropertyTextState
from ...graphics.items.mixin import ItemMixin

from ..components.layout.ok_cancel import OkCancelLayout

from .item_type import (
    PropertiesItemTypeWidget, PropertiesItemTypeTabWidget
)


@dataclass
class StoreText:
    source  : PropertyTextItem  | None # None if new
    initial : PropertyTextState | None = None
    current : PropertyTextState | None = None
    deleted : bool = False

    def __post_init__(self : Self) -> None:
        if self.initial is None and self.source is not None:
            self.initial = self.source.state()
        if self.current is None and self.initial is not None:
            self.current = replace(self.initial)


@dataclass
class StoreProperty:
    source  : Property      | None         # None if new
    texts   : list[StoreText]
    initial : PropertyState | None = None  # original name lives here
    current : PropertyState | None = None  # rename edits current.name
    deleted : bool = False

    def __post_init__(self : Self) -> None:
        if self.initial is None and self.source is not None:
            self.initial = self.source.state()
        if self.current is None and self.initial is not None:
            self.current = replace(self.initial)


class PropertiesDialog(QDialog):
    """
    Dialog for editing properties.
    """

    _main_widget : PropertiesItemTypeWidget | PropertiesItemTypeTabWidget
    _store       : dict[PropertiesMixin, list[StoreProperty]]

    def __init__(
        self   : Self,
        owners : list[PropertiesMixin],
        parent : QWidget | None = None
    ) -> None:
        # initialize dialo
        super().__init__(parent)
        # check for no items
        if len(owners) == 0:
            raise ValueError("No items")
        for owner in owners:
            if not isinstance(owner, ItemMixin):
                raise ValueError(f"Item {owner} is not a ItemMixin")
        # a property text is its own owner only if its parent is not already here
        owner_set = set(owners)
        owners = [
            owner for owner in owners
            if not isinstance(owner, PropertyTextItem)
            or (parent := owner.owner()) is None
            or parent not in owner_set
        ]
        # process items
        # exclude property texts whose parent is present
        shit
        # build subnets and nets and net labels from connection segments
        shit


        # process items into items_dict
        owners_dict : dict[str, list[PropertiesMixin]] = {}
        for owner in owners:
            owner_type_name = owner.description()
            owners_dict.setdefault(owner_type_name, []).append(owner)
        # build store of property and text states
        self._store = {}
        for owner in owners:
            self._store[owner] = []
            for property in owner.properties.values():
                texts = owner.propertyTextItems(property)
                store_texts = [StoreText(text) for text in texts]
                store_property = StoreProperty(property, store_texts)
                self._store[owner].append(store_property)
        # set window title
        item_types = list(owners_dict.keys())
        if len(owners) == 1:
            title = f"{item_types[0]} Properties"
        elif len(item_types) == 1:
            title = f"{item_types[0]} Properties ({len(owners)} items)"
        else:
            title = f"Properties ({len(owners)} items)"
        self.setWindowTitle(title)
        # create main widget
        if len(owners_dict.keys()) == 1:
            self._main_widget = PropertiesItemTypeWidget(owners)
        else:
            self._main_widget = PropertiesItemTypeTabWidget()
            for owner_type_name in owners_dict.keys():
                self._main_widget.addTab(
                    PropertiesItemTypeWidget(owners_dict[owner_type_name]),
                    owner_type_name
                )
        # buttons
        ok_cancel_layout = OkCancelLayout(self)
        # create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._main_widget)
        layout.addLayout(ok_cancel_layout)
        self.setLayout(layout)
