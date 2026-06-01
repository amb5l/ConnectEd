"""Unit tests for AI ref registry."""

import json

import pytest

from ConnectEd.ai.refs import RefRegistry, refKind, toolError, toolOk

def test_tool_error_and_ok_json() -> None:
    err = json.loads(toolError("nope"))
    assert err == {"ok": False, "error": "nope"}
    ok = json.loads(toolOk(ref="mdi:1", title="Design"))
    assert ok == {"ok": True, "ref": "mdi:1", "title": "Design"}


def test_issue_and_resolve_plain_object() -> None:
    registry = RefRegistry()
    target = object()
    ref = registry.issue("mdi", target)
    assert ref == "mdi:1"
    assert refKind(ref) == "mdi"
    assert registry.resolve(ref) is target
    assert registry.resolve(ref, kind="mdi") is target
    assert registry.resolve(ref, kind="scene") is None


def test_resolve_unknown_or_malformed_ref() -> None:
    registry = RefRegistry()
    assert registry.resolve("mdi:99") is None
    assert registry.resolve("not-a-ref") is None


def test_drop_removes_ref() -> None:
    registry = RefRegistry()
    ref = registry.issue("item", {"x": 1})
    registry.drop(ref)
    assert registry.resolve(ref) is None


def test_issue_rejects_invalid_kind() -> None:
    registry = RefRegistry()
    with pytest.raises(ValueError):
        registry.issue("", object())
    with pytest.raises(ValueError):
        registry.issue("bad:kind", object())
