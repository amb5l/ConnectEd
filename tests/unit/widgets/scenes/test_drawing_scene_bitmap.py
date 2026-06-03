"""Unit tests for DrawingScene.bitmap()."""

import pytest

from PyQt6.QtCore    import QBuffer, QIODevice, QPointF, QSizeF
from PyQt6.QtGui     import QImage
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.widgets.graphics.items.rectangle import RectangleItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def test_diagram_bitmap_matches_sheet_size(connect_ed_app : ConnectEdApp) -> None:
    scene = DiagramScene()
    image = scene.bitmap()

    assert isinstance(image, QImage)
    assert image.width()  == int(scene.sheet.rect.width())
    assert image.height() == int(scene.sheet.rect.height())


def test_bitmap_encodes_as_png(connect_ed_app : ConnectEdApp) -> None:
    scene = DiagramScene()
    image = scene.bitmap()

    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, b"PNG")
    assert len(buffer.data()) > 0


def test_drawing_bitmap_uses_item_bounds(connect_ed_app : ConnectEdApp) -> None:
    scene = DrawingScene()
    rect  = RectangleItem(QPointF(20.0, 30.0), QSizeF(40.0, 50.0))
    scene.addItem(rect)

    image  = scene.bitmap()
    source = scene._bitmapSourceRect()

    assert image.width()  == int(source.width())
    assert image.height() == int(source.height())
    assert source.width()  >= 40.0
    assert source.height() >= 50.0
