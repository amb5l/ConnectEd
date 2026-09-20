from __future__ import annotations

from typing      import Self
from dataclasses import dataclass, replace

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QGraphicsItem, QGraphicsScene

from ...graphics.properties import Property, PropertyState, PropertiesMixin

from ...graphics.scenes.diagram import DiagramScene

from ...graphics.items.role          import FunctionalItem, DecorativeItem
from ...graphics.items.property_text import PropertyTextItem, PropertyTextState
from ...graphics.items.segment       import SegmentItem
from ...graphics.items.node          import NodeItem

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
        items  : list[QGraphicsItem | QGraphicsScene],
        parent : QWidget | None = None
    ) -> None:
        # initialize dialog
        super().__init__(parent)
        # check for no items
        if len(items) == 0:
            raise ValueError("No items")
        # process/filter items
        item_set = set(items)
        filtered_items = []
        for item in items:
            # exclude chrome
            if not isinstance(item, FunctionalItem | DecorativeItem):
                continue
            # handle segments and nodes
            if isinstance(item, NodeItem):
                if not isinstance((scene := item.scene()), DiagramScene):
                    continue
                subnet = scene.netlist.nodeSubnet(item)
                net = scene
            if isinstance(item, SegmentItem):
                if not isinstance((scene := item.scene()), DiagramScene):
                    continue
                net = scene.netlist.segmentNet(item)
                if net is None:
                    continue
                subnet = scene.netlist.nodeSubnet(net)
                if subnet is None:
                    continue
                net = subnet.net
                continue
            # filter property texts
            if isinstance(item, PropertyTextItem):
                # exclude scene property texts
                if (owner := item.owner()) is None:
                    continue
                # exclude property texts whose parent is present
                if owner in item_set:
                    continue
            filtered_items.append(item)
        # build subnets and nets and net labels from connection segments
        shit


        # process items into items_dict
        owners_dict : dict[str, list[PropertiesMixin]] = {}
        for item in items:
            owner_type_name = item.description()
            owners_dict.setdefault(owner_type_name, []).append(item)
        # build store of property and text states
        self._store = {}
        for item in items:
            self._store[item] = []
            for property in item.properties.values():
                texts = item.propertyTextItems(property)
                store_texts = [StoreText(text) for text in texts]
                store_property = StoreProperty(property, store_texts)
                self._store[item].append(store_property)
        # set window title
        item_types = list(owners_dict.keys())
        if len(items) == 1:
            title = f"{item_types[0]} Properties"
        elif len(item_types) == 1:
            title = f"{item_types[0]} Properties ({len(items)} items)"
        else:
            title = f"Properties ({len(items)} items)"
        self.setWindowTitle(title)
        # create main widget
        if len(owners_dict.keys()) == 1:
            self._main_widget = PropertiesItemTypeWidget(items)
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
