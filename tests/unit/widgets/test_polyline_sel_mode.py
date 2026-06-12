"""Polyline selection mode resets on select/deselect transitions."""

import logging

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.widgets.graphics.items.polyline import PolylineItem
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


def _polyline(scene : DrawingScene) -> PolylineItem:
    item = PolylineItem(
        QPointF(0.0, 0.0),
        vertices = [QPointF(100.0, 0.0), QPointF(100.0, 100.0)],
    )
    scene.addItem(item)
    return item


def test_polyline_sel_mode_resets_on_select(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DrawingScene()
    item = _polyline(scene)
    item.setSelectMode(1)

    item.setSelected(True)

    assert item.selectMode() == 0


def test_polyline_sel_mode_resets_on_deselect(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DrawingScene()
    item = _polyline(scene)
    item.setSelected(True)
    item.setSelectMode(1)

    item.setSelected(False)

    assert item.selectMode() == 0


def test_polyline_loaded_starts_in_outline_mode(
    connect_ed_app : ConnectEdApp,
) -> None:
    item = PolylineItem(fresh = False)
    assert item.selectMode() == 0


def test_polyline_new_vertex_grips_visible_in_edit_mode(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DrawingScene()
    item = PolylineItem(
        QPointF(0.0, 0.0),
        vertices = [QPointF(100.0, 0.0)],
    )
    scene.addItem(item)
    item.setSelected(True)
    item.setSelectMode(1)

    item.addVertex(QPointF(200.0, 0.0))

    assert item.vertex(2).isVisible()
    assert item.segment(1).isVisible()
