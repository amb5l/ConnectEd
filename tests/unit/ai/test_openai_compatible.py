"""Unit tests for OpenAI-compatible message conversion."""

from ConnectEd.ai.providers.openai_compatible import _toOpenaiMessages
from ConnectEd.ai.types import ChatMessage, ToolCall


def test_assistant_tool_calls_round_trip() -> None:
    messages = [
        ChatMessage("user", "hello"),
        ChatMessage(
            "assistant",
            "",
            tool_calls = [
                ToolCall(id="call-1", name="ping", arguments={}),
            ],
        ),
        ChatMessage(
            "tool",
            '{"message":"ok"}',
            tool_call_id = "call-1",
            tool_name    = "ping",
        ),
    ]
    openai_messages = _toOpenaiMessages(messages)
    assert openai_messages[1]["role"] == "assistant"
    assert openai_messages[1]["tool_calls"][0]["function"]["name"] == "ping"
    assert openai_messages[2]["role"] == "tool"
    assert openai_messages[2]["tool_call_id"] == "call-1"
