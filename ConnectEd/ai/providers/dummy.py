"""Dummy AI provider — getting-started replies and optional demo tool loop."""

import json
from collections.abc import Iterator

from ..types import ChatEvent, ChatEventType, ChatMessage, ToolCall, ToolDefinition

_CONFIGURE_REPLY = (
    "No AI model is configured yet. Open AI Settings from the welcome message "
    "above (or AI → Settings…) and choose a provider, model, and API key. "
    "Send \"demo\" to run the nobodyHome() tool-call smoke test."
)


class DummyProvider:
    @staticmethod
    def chat(
        messages : list[ChatMessage],
        tools    : list[ToolDefinition],
    ) -> Iterator[ChatEvent]:
        if not messages:
            yield ChatEvent(ChatEventType.DONE)
            return

        last = messages[-1]

        if last.role == "tool":
            payload = json.loads(last.content)
            text = payload.get("message", last.content)
            yield ChatEvent(ChatEventType.TOKEN, f"nobodyHome() returned: {text}")
            yield ChatEvent(ChatEventType.DONE)
            return

        if last.role == "user" and last.content.strip().lower() == "demo":
            yield ChatEvent(
                ChatEventType.TOOL_CALL,
                tool_call = ToolCall(
                    id        = "dummy-nobody-home",
                    name      = "nobodyHome",
                    arguments = {},
                ),
            )
            yield ChatEvent(ChatEventType.DONE)
            return

        yield ChatEvent(ChatEventType.TOKEN, _CONFIGURE_REPLY)
        yield ChatEvent(ChatEventType.DONE)
