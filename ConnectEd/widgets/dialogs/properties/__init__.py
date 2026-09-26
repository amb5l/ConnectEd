from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QGraphicsItem

from ....core.check                  import checked

from ...graphics.properties          import (
    PropertyPending, PropertyAndTextsEdit, PropertiesMixin
)

from ...graphics.items.property_text import PropertyTextItem

from ..components.layout.ok_cancel   import OkCancelLayout

from .editor                         import (
    PropertiesEditorWidget, PropertiesEditorTabWidget
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.scenes.diagram import DiagramScene


OwnerStore = dict[PropertiesMixin, list[PropertyPending]]


class PropertiesDialog(QDialog):
    """
    Dialog for editing properties.
    """

    _store       : dict[str, OwnerStore]
    _main_widget : PropertiesEditorWidget | PropertiesEditorTabWidget

    @checked
    def __init__(
        self   : Self,
        owners : list[QGraphicsItem] | list[DiagramScene],
        parent : QWidget             | None = None
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
                    property_draft = PropertyPending(property)
                    self._store[owner_type_name][owner].append(property_draft)
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
            self._main_widget = PropertiesEditorWidget(owner_store)
        else:
            self._main_widget = PropertiesEditorTabWidget(self._store)
        # buttons
        ok_cancel_layout = OkCancelLayout(self)
        # create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._main_widget)
        layout.addLayout(ok_cancel_layout)
        self.setLayout(layout)

    @checked
    def getEdits(self : Self) -> list[PropertyAndTextsEdit]:
        edits : list[PropertyAndTextsEdit] = []
        for owner_store in self._store.values():
            for owner, store_properties in owner_store.items():
                for store_property in store_properties:
                    if (edit := store_property.getEdit(owner)) is not None:
                        edits.append(edit)
        return edits
