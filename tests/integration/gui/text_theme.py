"""Check that a text item's Qt renderer matches its theme quill."""

from __future__ import annotations

from PyQt6.QtWidgets import QGraphicsScene

from ConnectEd.widgets.graphics.items.base_text import BaseTextItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene


def assert_text_theme(
    item     : BaseTextItem,
    expected : str,
    scene    : QGraphicsScene | None = None,
) -> None:
    """Rendered string, and font and color on the Qt text item."""
    if scene is None:
        scene = item.scene()
    assert isinstance(scene, DiagramScene), "text item has no diagram scene"
    child = item._child
    assert child.text() == expected, (
        f"{item.resourcesName()} text {child.text()!r}, expected {expected!r}"
    )
    quill = scene.resources.quill(item.resourcesName(), False)
    assert child.color() == quill.color(), (
        f"{item.resourcesName()} color {child.color().name()} "
        f"!= theme {quill.color().name()}"
    )
    font = child.font()
    assert font.family() == quill.font()
    assert abs(font.pointSizeF() - quill.size()) < 0.01
    assert font.bold() is quill.bold()
    assert font.italic() is quill.italic()
    assert font.underline() is quill.underline()
