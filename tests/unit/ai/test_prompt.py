"""Unit tests for AI system prompt assembly."""

import pytest

from ConnectEd.ai.prompt import buildSystemPrompt, formatToolsForPrompt
from ConnectEd.ai.types import ToolDefinition


def test_format_tools_for_prompt_lists_names() -> None:
    tools = [
        ToolDefinition(
            name        = "ping",
            description = "Health check.",
            parameters  = {"type": "object", "properties": {}},
        )
    ]
    text = formatToolsForPrompt(tools)
    assert "**ping**" in text
    assert "Health check." in text


def test_build_system_prompt_includes_connect_ed_and_tools(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    class _FakeSettings:
        def get(self, path : str) -> str:
            return ""

    monkeypatch.setattr("ConnectEd.ai.prompt.settings", lambda: _FakeSettings())
    tools = [
        ToolDefinition(
            name        = "ping",
            description = "Health check.",
            parameters  = {"type": "object", "properties": {}},
        )
    ]
    prompt = buildSystemPrompt(tools, diagram_summary = "Empty canvas")
    assert "ConnectEd" in prompt
    assert "**ping**" in prompt
    assert "Empty canvas" in prompt
    assert "Do not invent tools" in prompt


def test_build_system_prompt_appends_user_extra(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    class _FakeSettings:
        def get(self, path : str) -> str:
            if path == "ai/system_prompt_extra":
                return "Prefer metric units."
            return ""

    monkeypatch.setattr("ConnectEd.ai.prompt.settings", lambda: _FakeSettings())
    prompt = buildSystemPrompt([])
    assert "Prefer metric units." in prompt
    assert "### User instructions" in prompt
