"""Anthropic Claude provider."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import anthropic

from ..types import ChatEvent, ChatEventType, ChatMessage, ToolCall, ToolDefinition


DEFAULT_API_KEY_NAME = "$ANTHROPIC_API_KEY"


def listModels(api_key : str, _base_url : str = "") -> list[str]:
    if not api_key:
        return []
    client = anthropic.Anthropic(api_key=api_key)
    response = client.models.list()
    models = [model for model in response.data if model.id]
    models.sort(
        key = lambda model : getattr(model, "created_at", 0) or 0,
        reverse = True,
    )
    return [model.id for model in models]


def _toolDefinitions(tools : list[ToolDefinition]) -> list[dict[str, Any]] | None:
    if not tools:
        return None
    return [
        {
            "name"         : tool.name,
            "description"  : tool.description,
            "input_schema" : tool.parameters,
        }
        for tool in tools
    ]


def _toAnthropicMessages(
    messages : list[ChatMessage],
) -> tuple[str | None, list[dict[str, Any]]]:
    system_parts : list[str] = []
    anthropic_messages : list[dict[str, Any]] = []

    for message in messages:
        if message.role == "system":
            system_parts.append(message.content)
        elif message.role == "user":
            anthropic_messages.append({
                "role"    : "user",
                "content" : message.content,
            })
        elif message.role == "assistant":
            anthropic_messages.append({
                "role"    : "assistant",
                "content" : message.content,
            })
        elif message.role == "tool":
            anthropic_messages.append({
                "role"    : "user",
                "content" : [{
                    "type"        : "tool_result",
                    "tool_use_id" : message.tool_call_id or "",
                    "content"     : message.content,
                }],
            })

    system = "\n".join(system_parts) if system_parts else None
    return system, anthropic_messages


class AnthropicProvider:
    _api_key : str
    _model   : str

    def __init__(
        self,
        api_key  : str = "",
        base_url : str = "",
        model    : str = "",
        **_kwargs : Any,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required for Anthropic")
        if not model:
            raise ValueError("model is required for Anthropic")
        self._api_key = api_key
        self._model   = model
        self._base_url = base_url

    def chat(
        self,
        messages : list[ChatMessage],
        tools    : list[ToolDefinition],
    ) -> Iterator[ChatEvent]:
        if not messages:
            yield ChatEvent(ChatEventType.DONE)
            return

        client_kwargs : dict[str, Any] = {"api_key" : self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url
        client = anthropic.Anthropic(**client_kwargs)

        system, anthropic_messages = _toAnthropicMessages(messages)
        request_kwargs : dict[str, Any] = {
            "model"      : self._model,
            "messages"   : anthropic_messages,
            "max_tokens" : 4096,
        }
        if system:
            request_kwargs["system"] = system
        tool_defs = _toolDefinitions(tools)
        if tool_defs:
            request_kwargs["tools"] = tool_defs

        try:
            with client.messages.stream(**request_kwargs) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        delta = event.delta
                        if getattr(delta, "type", None) == "text_delta":
                            yield ChatEvent(ChatEventType.TOKEN, delta.text)
                    elif event.type == "content_block_start":
                        block = event.content_block
                        if getattr(block, "type", None) == "tool_use":
                            yield ChatEvent(
                                ChatEventType.TOOL_CALL,
                                tool_call = ToolCall(
                                    id        = block.id,
                                    name      = block.name,
                                    arguments = block.input or {},
                                ),
                            )
        except Exception as exc:
            yield ChatEvent(ChatEventType.ERROR, error=str(exc))
            yield ChatEvent(ChatEventType.DONE)
            return

        yield ChatEvent(ChatEventType.DONE)
