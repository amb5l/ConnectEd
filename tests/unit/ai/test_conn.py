"""Unit tests for add_connection AI tool."""

import json
from unittest.mock import MagicMock

from PyQt6.QtCore import QPointF

from ConnectEd.ai.refs import RefRegistry
from ConnectEd.ai.tools.conn import add_connection


def test_add_connection_routes_hv_legs(monkeypatch) -> None:
    scene = MagicMock()
    scene.undo_stack.beginMacro = MagicMock()
    scene.undo_stack.endMacro   = MagicMock()
    add_segment_calls : list[tuple[QPointF, QPointF]] = []

    def record_segment(p1 : QPointF, p2 : QPointF, undoable : bool = False) -> None:
        add_segment_calls.append((QPointF(p1), QPointF(p2)))

    scene.addSegment.side_effect = record_segment

    monkeypatch.setattr(
        "ConnectEd.ai.tools.conn._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )

    result = json.loads(add_connection(
        MagicMock(),
        RefRegistry(),
        {
            "view"    : "view:1",
            "start"   : {"x": 100.0, "y": 50.0},
            "offsets" : [
                {"axis": "H", "delta": 40.0},
                {"axis": "V", "delta": -10.0},
            ],
        },
    ))

    assert result == {"ok": True, "end_x": 140.0, "end_y": 40.0, "legs": 2}
    assert len(add_segment_calls) == 2
    assert add_segment_calls[0][0] == QPointF(100.0, 50.0)
    assert add_segment_calls[0][1] == QPointF(140.0, 50.0)
    assert add_segment_calls[1][0] == QPointF(140.0, 50.0)
    assert add_segment_calls[1][1] == QPointF(140.0, 40.0)
    scene.undo_stack.beginMacro.assert_called_once_with("addConnection")
    scene.netlistChanged.emit.assert_called_once()


def test_add_connection_rejects_diagonal_offset_spec() -> None:
    result = json.loads(add_connection(
        MagicMock(),
        RefRegistry(),
        {
            "view"    : "view:1",
            "start"   : {"x": 0.0, "y": 0.0},
            "offsets" : [{"axis": "X", "delta": 10.0}],
        },
    ))
    assert result["ok"] is False
    assert "axis" in result["error"]


def test_add_connection_requires_start() -> None:
    result = json.loads(add_connection(
        MagicMock(),
        RefRegistry(),
        {
            "view"    : "view:1",
            "offsets" : [{"axis": "H", "delta": 10.0}],
        },
    ))
    assert result == {"ok": False, "error": "start or start_ref is required"}


def test_add_connection_start_ref_resolves_point(monkeypatch) -> None:
    scene = MagicMock()
    scene.undo_stack.beginMacro = MagicMock()
    scene.undo_stack.endMacro   = MagicMock()

    monkeypatch.setattr(
        "ConnectEd.ai.tools.conn._drawingSceneFromViewRef",
        lambda registry, view: (scene, None),
    )
    monkeypatch.setattr(
        "ConnectEd.ai.tools.conn._startFromItemRef",
        lambda registry, start_ref: (QPointF(5.0, 6.0), None),
    )

    result = json.loads(add_connection(
        MagicMock(),
        RefRegistry(),
        {
            "view"      : "view:1",
            "start_ref" : "item:1",
            "offsets"   : [{"axis": "V", "delta": 4.0}],
        },
    ))

    assert result["ok"] is True
    assert result["end_x"] == 5.0
    assert result["end_y"] == 10.0
    scene.addSegment.assert_called_once()
    call = scene.addSegment.call_args[0]
    assert call[0] == QPointF(5.0, 6.0)
    assert call[1] == QPointF(5.0, 10.0)
