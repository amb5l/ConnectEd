"""Unit tests for AI tool implementations."""

import builtins
import json
from types import UnionType
from unittest.mock import MagicMock

from PyQt6.QtCore import QPointF, QRectF

from ConnectEd.ai.refs import RefRegistry
from ConnectEd.ai.tools.get import get_items, get_sheet, set_sheet
from ConnectEd.widgets.graphics.items.mixin import ItemMixin
from ConnectEd.widgets.graphics.items.node import NodeItem
from ConnectEd.widgets.graphics.items.segment import SegmentItem

_real_isinstance = builtins.isinstance


def test_get_diagram_sheet_returns_layout(monkeypatch) -> None:
    scene = MagicMock()
    scene.getSheetName.return_value = "A4 (landscape)"
    scene.getSheetWidth.return_value = 297.0
    scene.getSheetHeight.return_value = 210.0
    scene.getMargin.return_value = 10.0
    scene.getBorder.return_value = 1.0

    monkeypatch.setattr(
        "ConnectEd.ai.tools.get._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )

    result = json.loads(get_sheet(
        MagicMock(),
        RefRegistry(),
        {"view": "view:1"},
    ))
    assert result == {
        "ok"     : True,
        "name"   : "A4 (landscape)",
        "left"   : 0.0,
        "top"    : 0.0,
        "width"  : 297.0,
        "height" : 210.0,
        "margin" : 10.0,
        "border" : 1.0,
    }


def test_get_diagram_sheet_stale_ref() -> None:
    result = json.loads(get_sheet(
        MagicMock(),
        RefRegistry(),
        {"view": "view:99"},
    ))
    assert result["ok"] is False
    assert "view" in result["error"].lower()


def test_get_diagram_sheet_missing_view() -> None:
    result = json.loads(get_sheet(MagicMock(), RefRegistry(), {}))
    assert result == {"ok": False, "error": "view is required"}


def test_set_sheet_updates_dimensions(monkeypatch) -> None:
    scene = MagicMock()
    scene.getSheetWidth.return_value = 400.0
    scene.getSheetHeight.return_value = 300.0

    monkeypatch.setattr(
        "ConnectEd.ai.tools.get._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )

    result = json.loads(set_sheet(
        MagicMock(),
        RefRegistry(),
        {"view": "view:1", "width": 400.0, "height": 300.0},
    ))
    scene.setSheetWidth.assert_called_once_with(400.0)
    scene.setSheetHeight.assert_called_once_with(300.0)
    assert result == {"ok": True, "width": 400.0, "height": 300.0}


def test_set_sheet_rejects_non_positive_size(monkeypatch) -> None:
    scene = MagicMock()
    monkeypatch.setattr(
        "ConnectEd.ai.tools.get._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )
    result = json.loads(set_sheet(
        MagicMock(),
        RefRegistry(),
        {"view": "view:1", "width": 0.0, "height": 100.0},
    ))
    assert result["ok"] is False
    scene.setSheetWidth.assert_not_called()


def test_get_items_returns_bounds(monkeypatch) -> None:
    item = MagicMock()
    item.parentItem.return_value = None
    item.scenePos.return_value = QPointF(10.0, 20.0)
    item.boundingRect.return_value = QRectF(0.0, 0.0, 50.0, 30.0)
    mapped = MagicMock()
    mapped.boundingRect.return_value = QRectF(10.0, 20.0, 50.0, 30.0)
    item.mapToScene.return_value = mapped
    item.settingsName.return_value = "Block"

    def isinstance_stub(obj, cls) -> bool:
        if obj is item:
            if cls is ItemMixin:
                return True
            if cls in (NodeItem, SegmentItem):
                return False
            if _real_isinstance(cls, UnionType):
                return False
        return _real_isinstance(obj, cls)

    scene = MagicMock()
    scene.items.return_value = [item]

    monkeypatch.setattr(builtins, "isinstance", isinstance_stub)
    monkeypatch.setattr(
        "ConnectEd.ai.tools.get._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )

    result = json.loads(get_items(
        MagicMock(),
        RefRegistry(),
        {"view": "view:1"},
    ))
    assert result["ok"] is True
    assert len(result["items"]) == 1
    row = result["items"][0]
    assert row["kind"] == "Block"
    assert row["x"] == 10.0
    assert row["y"] == 20.0
    assert row["left"] == 10.0
    assert row["top"] == 20.0
    assert row["width"] == 50.0
    assert row["height"] == 30.0
    assert row["ref"].startswith("item:")
