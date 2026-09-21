from __future__ import annotations

from typing      import Self
from dataclasses import dataclass, replace

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QGraphicsItem

from ....core.check import checked

from ...graphics.properties import (
    Property, PropertyState,
    PropertyChange, PropertyAdd, PropertyDelete,
    PropertiesMixin
)

from ...graphics.items.property_text import (
    PropertyTextItem, PropertyTextState,
    PropertyTextChange, PropertyTextAdd, PropertyTextDelete
)

from ..components.layout.ok_cancel import OkCancelLayout

from .item_type import (
    PropertiesItemTypeWidget, PropertiesItemTypeTabWidget
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.scenes.diagram import DiagramScene


@dataclass
class StorePropertyText:
    obj     : PropertyTextItem  | None  # None if new
    current : PropertyTextState
    initial : PropertyTextState | None
    deleted : bool

    @checked
    def __init__(
        self   : Self,
        source : PropertyTextItem | PropertyTextState
    ) -> None:
        if isinstance(source, PropertyTextItem):
            self.obj     = source
            self.initial = source.state()
            self.current = replace(self.initial)
            self.deleted = False
        else:
            self.obj     = None
            self.current = source
            self.initial = None
            self.deleted = False


@dataclass
class StoreProperty:
    obj     : Property | None  # None if new
    current : PropertyState
    initial : PropertyState | None
    deleted : bool
    texts   : list[StorePropertyText]

    @checked
    def __init__(
        self   : Self,
        source : Property | PropertyState,
        texts  : list[StorePropertyText] | None = None
    ) -> None:
        if isinstance(source, Property):
            self.obj     = source
            self.initial = source.state()
            self.current = replace(self.initial)
            self.deleted = False
        else:
            self.obj     = None
            self.current = source
            self.initial = None
            self.deleted = False
        self.texts = texts or []


OwnerStore = dict[PropertiesMixin, list[StoreProperty]]

PropertiesChange = \
    PropertyChange     | \
    PropertyAdd        | \
    PropertyDelete     | \
    PropertyTextChange | \
    PropertyTextAdd    | \
    PropertyTextDelete


class PropertiesDialog(QDialog):
    """
    Dialog for editing properties.
    """

    _store : dict[str, OwnerStore]
    _main_widget : PropertiesItemTypeWidget | PropertiesItemTypeTabWidget

    @checked
    def __init__(
        self   : Self,
        owners : list[QGraphicsItem] | list[DiagramScene],
        parent : QWidget | None = None
    ) -> None:
        # initialize dialog
        super().__init__(parent)
        # check for no owners
        if len(owners) == 0:
            raise ValueError("No items")
        # process/filter owners
        owner_set = set(owners)
        clean_owners : list[PropertiesMixin] = []
        for owner in owner_set:
            if not isinstance(owner, PropertiesMixin):
                continue
            if isinstance(owner, PropertyTextItem):
                # exclude scene property texts
                if (pt_owner := owner.owner()) is None:
                    continue
                # exclude property texts whose parent is present
                if pt_owner in owner_set:
                    continue
            clean_owners.append(owner)
        # process items into items_dict
        owner_dict : dict[str, list[PropertiesMixin]] = {}
        for owner in clean_owners:
            owner_type_name = owner.description()
            owner_dict.setdefault(owner_type_name, []).append(owner)
        # build store of property and text states for each owner type
        self._store = {}
        for owner_type_name in owner_dict.keys():
            self._store[owner_type_name] = {}
            for owner in owner_dict[owner_type_name]:
                self._store[owner_type_name][owner] = []
                for property in owner.properties.values():
                    texts = owner.propertyTextItems(property)
                    store_texts = [StorePropertyText(text) for text in texts]
                    store_property = StoreProperty(property, store_texts)
                    self._store[owner_type_name][owner].append(store_property)
        # set window title
        item_types = list(owner_dict.keys())
        if len(owners) == 1:
            title = f"{item_types[0]} Properties"
        elif len(item_types) == 1:
            title = f"{item_types[0]} Properties ({len(owners)} items)"
        else:
            title = f"Properties ({len(owners)} items)"
        self.setWindowTitle(title)
        # create main widget
        if len(owner_dict.keys()) == 1:
            owner_store = list(self._store.values())[0]
            self._main_widget = PropertiesItemTypeWidget(owner_store)
        else:
            self._main_widget = PropertiesItemTypeTabWidget(self._store)
        # buttons
        ok_cancel_layout = OkCancelLayout(self)
        # create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._main_widget)
        layout.addLayout(ok_cancel_layout)
        self.setLayout(layout)

    @checked
    def getEdits(self : Self) -> list[PropertiesChange]:
        edits : list[PropertiesChange] = []
        for owner_store in self._store.values():
            for owner, store_properties in owner_store.items():
                for store_property in store_properties:
                    if store_property.obj is None:
                        if not store_property.deleted:
                            edits.append(PropertyAdd(
                                owner,
                                store_property.current,
                                [
                                    text.current
                                    for text in store_property.texts
                                    if text.obj is None and not text.deleted
                                ]
                            ))
                        continue
                    if store_property.deleted:
                        edits.append(PropertyDelete(
                            owner, store_property.obj
                        ))
                        continue
                    if store_property.initial is not None:
                        change = PropertyChange.fromComparison(
                            owner,
                            store_property.obj,
                            store_property.initial,
                            store_property.current
                        )
                        if not change.noop():
                            edits.append(change)
                    for text in store_property.texts:
                        if text.obj is None:
                            if not text.deleted:
                                edits.append(PropertyTextAdd(
                                    owner, store_property.obj, text.current
                                ))
                            continue
                        elif text.deleted:
                            edits.append(PropertyTextDelete(text.obj))
                            continue
                        elif text.initial is None:
                            continue
                        text_change = PropertyTextChange.fromComparison(
                            text.obj, text.initial, text.current
                        )
                        if not text_change.noop():
                            edits.append(text_change)
        return edits
