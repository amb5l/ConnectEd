"""Order-independent diagram scene comparison (ConnectEd properties contract)."""

from __future__ import annotations

from typing import Any, Callable

from ConnectEd.core.utils import val2str
from ConnectEd.widgets.graphics.items.mixin.xml import ItemXmlMixin
from ConnectEd.widgets.graphics.items.node import NodeItem
from ConnectEd.widgets.graphics.items.segment import SegmentItem
from ConnectEd.widgets.graphics.properties import PropertiesMixin
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene

SIGNATURE_EXTRAS: dict[type, Callable[..., Any]] = {}


def _normalize_value(value: Any) -> str:
    if value is None:
        return "None"
    try:
        return val2str(value)
    except (ValueError, TypeError):
        return repr(value)


def _worthy_properties(owner: PropertiesMixin) -> tuple[tuple[str, str], ...]:
    props = []
    for name in owner.properties.names():
        if not owner.properties.worthy(name):
            continue
        value = owner.properties.value(name)
        props.append((name, _normalize_value(value)))
    return tuple(sorted(props))


def _top_level_drawables(scene: DrawingScene) -> list[ItemXmlMixin]:
    items: list[ItemXmlMixin] = []
    for item in scene.items():
        if isinstance(item, NodeItem | SegmentItem):
            continue
        if item.parentItem() is not None:
            continue
        if isinstance(item, ItemXmlMixin):
            items.append(item)
    return items


def scene_signature(scene: DrawingScene) -> tuple[Any, ...]:
    """Serializable, order-independent scene snapshot."""
    scene_props = ("__scene__", _worthy_properties(scene))
    item_sigs = []
    for item in _top_level_drawables(scene):
        sig: list[Any] = [item.__class__.__name__, _worthy_properties(item)]
        extra = SIGNATURE_EXTRAS.get(type(item))
        if extra is not None:
            sig.append(extra(item))
        item_sigs.append(tuple(sig))
    return (scene_props,) + tuple(sorted(item_sigs))


def compare_scenes(expected: DrawingScene, actual: DrawingScene) -> None:
    expected_sig = scene_signature(expected)
    actual_sig = scene_signature(actual)
    assert actual_sig == expected_sig, (
        "scene mismatch after save/reload\n"
        f"expected: {expected_sig}\n"
        f"actual:   {actual_sig}"
    )
