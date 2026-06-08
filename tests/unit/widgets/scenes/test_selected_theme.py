"""Selected appearance: global defaults and sparse per-item overrides."""

import pytest
from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.widgets.graphics.items.node import NodeState
from ConnectEd.widgets.graphics.scenes.diagram.resources import DiagramSceneResources


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def test_free_node_selected_pen_uses_solid_line_override(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DiagramSceneResources()
    connected_sel = resources.pen("FreeNode", (NodeState.CONNECTED, True))
    assert connected_sel.style() == Qt.PenStyle.SolidLine
    unconnected_sel = resources.pen("FreeNode", (NodeState.UNCONNECTED, True))
    assert unconnected_sel.style() == Qt.PenStyle.SolidLine


def test_free_node_unselected_keeps_theme_style(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DiagramSceneResources()
    connected = resources.pen("FreeNode", (NodeState.CONNECTED, False))
    assert connected.style() == Qt.PenStyle.NoPen
