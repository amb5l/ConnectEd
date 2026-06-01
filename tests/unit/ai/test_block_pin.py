"""Unit tests for block pin AI tools."""

import json
from unittest.mock import MagicMock

from ConnectEd.ai.refs import RefRegistry
from ConnectEd.ai.tools.block_pin import (
    _directionFromTool,
    _edgeFromTool,
    _parsePinSpec,
    add_block_pin,
    add_block_pins,
)
from ConnectEd.core.types import Direction, Edge


def test_edge_from_tool() -> None:
    assert _edgeFromTool("left") == Edge.LEFT
    assert _edgeFromTool("TOP") == Edge.TOP
    assert _edgeFromTool("bad") is None


def test_direction_from_tool() -> None:
    assert _directionFromTool("in") == Direction.IN
    assert _directionFromTool("OUT") == Direction.OUT
    assert _directionFromTool("bi") == Direction.BI
    assert _directionFromTool("invalid") is None


def test_parse_pin_spec_ok() -> None:
    spec, err = _parsePinSpec({
        "name"      : "clk",
        "direction" : "in",
        "edge"      : "left",
        "offset"    : 20,
    })
    assert err is None
    assert spec == {
        "name"      : "clk",
        "direction" : Direction.IN,
        "edge"      : Edge.LEFT,
        "offset"    : 20.0,
    }


def test_add_block_pins_places_all(monkeypatch) -> None:
    block = MagicMock()
    scene = MagicMock()
    registry = RefRegistry()
    registry.issue("item", block)
    view_ref = registry.issue("view", MagicMock())

    pin_instances : list[MagicMock] = []

    class FakePin:
        def __init__(self, _parent=None) -> None:
            self._name = ""
            self._calls : list[tuple] = []

        def setName(self, name : str) -> None:
            self._name = name

        def setDirection(self, direction) -> None:
            self._calls.append(("direction", direction))

        def setLocEdge(self, edge) -> None:
            self._calls.append(("edge", edge))

        def setLocOffset(self, offset : float) -> None:
            self._calls.append(("offset", offset))

    def fake_pin_factory(_parent=None) -> FakePin:
        pin = FakePin(_parent)
        pin_instances.append(pin)
        return pin

    monkeypatch.setattr(
        "ConnectEd.ai.tools.block_pin._drawingSceneFromViewRef",
        lambda _registry, _view: (scene, None),
    )
    monkeypatch.setattr(
        "ConnectEd.ai.tools.block_pin._resolveBlock",
        lambda _registry, _item: (block, None),
    )
    monkeypatch.setattr(
        "ConnectEd.widgets.graphics.items.block_pin.BlockPinItem",
        fake_pin_factory,
    )

    block_ref = list(registry._by_ref.keys())[0]
    result = json.loads(add_block_pins(
        MagicMock(),
        registry,
        {
            "view" : view_ref,
            "item" : block_ref,
            "pins" : [
                {
                    "name"      : "a",
                    "direction" : "in",
                    "edge"      : "left",
                    "offset"    : 0,
                },
                {
                    "name"      : "b",
                    "direction" : "out",
                    "edge"      : "right",
                    "offset"    : 10,
                },
            ],
        },
    ))
    assert result["ok"] is True
    assert len(result["pins"]) == 2
    assert result["pins"][0]["name"] == "a"
    assert scene.addBlockPin.call_count == 2
    assert pin_instances[0]._calls[0] == ("direction", Direction.IN)
    assert pin_instances[1]._calls[0] == ("direction", Direction.OUT)


def test_add_block_pin_invalid_edge() -> None:
    registry = RefRegistry()
    block_ref = registry.issue("item", MagicMock())
    view_ref = registry.issue("view", MagicMock())
    result = json.loads(add_block_pin(
        MagicMock(),
        registry,
        {
            "view"      : view_ref,
            "item"      : block_ref,
            "name"      : "x",
            "direction" : "in",
            "edge"      : "middle",
            "offset"    : 0,
        },
    ))
    assert result["ok"] is False
    assert "edge" in result["error"].lower()
