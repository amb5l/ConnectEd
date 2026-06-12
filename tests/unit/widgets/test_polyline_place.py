"""Regression: placed polylines must accept mouse hits after placement ends."""

import logging
import sys
import types
from pathlib import Path

import pytest
from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


def _import_place_interaction():
    """Avoid drawing<->window circular import during unit tests."""
    drawing_key = "ConnectEd.widgets.graphics.views.drawing"
    if drawing_key not in sys.modules:
        repo = Path(__file__).resolve().parents[3]
        drawing_dir = repo / "ConnectEd" / "widgets" / "graphics" / "views" / "drawing"
        stub = types.ModuleType(drawing_key)
        stub.__path__ = [str(drawing_dir)]
        stub.DrawingView = object
        stub.DrawingSubWindow = object
        sys.modules[drawing_key] = stub
    from ConnectEd.widgets.graphics.views.drawing.interaction.place import (
        DrawingPlacePolylineInteraction,
    )
    return DrawingPlacePolylineInteraction


class _FakeDrawingView:
    def __init__(self, scene : DrawingScene) -> None:
        self._scene = scene

    def scene(self) -> DrawingScene:
        return self._scene


def test_polyline_finish_restores_mouse_buttons(
    connect_ed_app : ConnectEdApp,
) -> None:
    DrawingPlacePolylineInteraction = _import_place_interaction()

    scene = DrawingScene()
    view = _FakeDrawingView(scene)
    p0 = QPointF(0.0, 0.0)
    p1 = QPointF(100.0, 0.0)
    p2 = QPointF(200.0, 0.0)

    interaction = DrawingPlacePolylineInteraction(view, p0)  # type: ignore[arg-type]
    item = interaction._item
    assert item.acceptedMouseButtons() == Qt.MouseButton.NoButton

    interaction.commit(p1)
    interaction.commit(p2)
    interaction.complete(p2)

    assert item.acceptedMouseButtons() != Qt.MouseButton.NoButton


def test_polyline_close_at_origin_restores_mouse_buttons(
    connect_ed_app : ConnectEdApp,
) -> None:
    DrawingPlacePolylineInteraction = _import_place_interaction()

    scene = DrawingScene()
    view = _FakeDrawingView(scene)
    p0 = QPointF(50.0, 50.0)
    p1 = QPointF(150.0, 50.0)

    interaction = DrawingPlacePolylineInteraction(view, p0)  # type: ignore[arg-type]
    item = interaction._item
    interaction.commit(p1)
    assert interaction.commit(p0)

    assert item.acceptedMouseButtons() != Qt.MouseButton.NoButton
    assert item.closed()
