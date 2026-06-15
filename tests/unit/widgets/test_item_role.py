"""Role markers: mutual exclusivity and registered-item coverage."""

import pytest

from ConnectEd.widgets.graphics.items import (
    _item_classes,
    DecorativeItem,
    DocumentItem,
    FunctionalItem,
)
from ConnectEd.widgets.graphics.items.net_label import NetLabelItem
from ConnectEd.widgets.graphics.items.text import BaseTextItem, TextItem


def test_decorative_and_functional_are_mutually_exclusive() -> None:
    with pytest.raises(TypeError, match="both DecorativeItem and FunctionalItem"):
        type(
            "BothRolesItem",
            (DecorativeItem, FunctionalItem, object),
            {},
        )


def test_functional_cannot_subclass_decorative_leaf() -> None:
    with pytest.raises(TypeError, match="both DecorativeItem and FunctionalItem"):
        type(
            "BadNetLabel",
            (FunctionalItem, TextItem),
            {},
        )


def test_text_and_net_label_roles() -> None:
    assert issubclass(TextItem, DecorativeItem)
    assert not issubclass(TextItem, FunctionalItem)
    assert issubclass(NetLabelItem, FunctionalItem)
    assert not issubclass(NetLabelItem, DecorativeItem)


def test_base_text_item_has_no_role_marker() -> None:
    assert not issubclass(BaseTextItem, DecorativeItem)
    assert not issubclass(BaseTextItem, FunctionalItem)


@pytest.mark.parametrize("item_name", list(_item_classes.keys()))
def test_registered_items_are_decorative_or_functional(item_name : str) -> None:
    item_cls = _item_classes[item_name]
    decorative = issubclass(item_cls, DecorativeItem)
    functional = issubclass(item_cls, FunctionalItem)
    assert decorative ^ functional, (
        f"{item_name} must be exactly one of DecorativeItem or FunctionalItem "
        f"(decorative={decorative}, functional={functional})"
    )
    assert issubclass(item_cls, DocumentItem)
