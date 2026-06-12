"""Block-format TextItem must honour horizontal alignment within a width constraint."""

import logging

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsSimpleTextItem

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.core.types import AlignH
from ConnectEd.widgets.graphics.items.text import TextItem, TextBlockRenderer
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


def _glyph_scene_rect(item : TextItem) -> tuple[float, float, float, float]:
    child = item._child
    if isinstance(child, TextBlockRenderer):
        rect = child.mapToScene(child.boundingRect()).boundingRect()
    else:
        rect = child.mapToScene(
            QGraphicsSimpleTextItem.boundingRect(child)
        ).boundingRect()
    return rect.left(), rect.right(), rect.top(), rect.bottom()


def test_block_text_center_align_within_width(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DrawingScene()
    item = TextItem(text="hello", pos=QPointF(100.0, 100.0), width=80.0)
    item.setBlock(True)
    item.setAlignH(AlignH.CENTER)
    scene.addItem(item)

    handle = item.mapToScene(item.handleRect()).boundingRect()
    left, right, _top, _bottom = _glyph_scene_rect(item)
    glyph_cx = (left + right) / 2
    handle_cx = (handle.left() + handle.right()) / 2

    assert handle.width() == pytest.approx(80.0, abs=0.5)
    assert glyph_cx == pytest.approx(handle_cx, abs=1.0)


def test_block_text_center_align_auto_width_multiline(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DrawingScene()
    item = TextItem(
        text="Destination Register\nData Source",
        pos=QPointF(100.0, 100.0),
    )
    item.setBlock(True)
    item.setAlignH(AlignH.CENTER)
    scene.addItem(item)

    child = item._child
    assert isinstance(child, TextBlockRenderer)
    doc = child.document()
    first = doc.begin()
    second = first.next()
    assert second.isValid()
    short_line = second.layout().lineAt(0)
    assert short_line.naturalTextWidth() < short_line.width()
    assert short_line.naturalTextRect().x() > 0.0

    handle = item.mapToScene(item.handleRect()).boundingRect()
    left, right, _top, _bottom = _glyph_scene_rect(item)
    assert (left + right) / 2 == pytest.approx(
        (handle.left() + handle.right()) / 2,
        abs=1.0,
    )
