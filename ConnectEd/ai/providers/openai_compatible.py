"""OpenAI-compatible chat provider (OpenAI SDK, xAI, Ollama, etc.)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

from openai import OpenAI

from ..types import ChatEvent, ChatEventType, ChatMessage, ToolCall, ToolSpec


def listModels(api_key : str, base_url : str) -> list[str]:
    if not base_url:
        return []
    client = OpenAI(
        api_key  = api_key or "unused",
        base_url = base_url,
    )
    response = client.models.list()
    models = [model for model in response.data if model.id]
    models.sort(
        key = lambda model : getattr(model, "created", 0) or 0,
        reverse = True,
    )
    return [model.id for model in models]


def _toolDefinitions(tools : list[ToolSpec]) -> list[dict[str, Any]] | None:
    if not tools:
        return None
    return [
        {
            "type"     : "function",
            "function" : {
                "name"        : tool.name,
                "description" : tool.description,
                "parameters"  : tool.parameters,
            },
        }
        for tool in tools
    ]


def _toOpenaiMessages(messages : list[ChatMessage]) -> list[dict[str, Any]]:
    openai_messages : list[dict[str, Any]] = []
    for message in messages:
        if message.role == "tool":
            openai_messages.append({
                "role"         : "tool",
                "content"      : message.content,
                "tool_call_id" : message.tool_call_id or "",
            })
        elif message.role == "assistant":
            entry : dict[str, Any] = {
                "role"    : "assistant",
                "content" : message.content or None,
            }
            if message.tool_calls:
                entry["content"] = message.content or None
                entry["tool_calls"] = [
                    {
                        "id"       : tool_call.id,
                        "type"     : "function",
                        "function" : {
                            "name"      : tool_call.name,
                            "arguments" : json.dumps(tool_call.arguments),
                        },
                    }
                    for tool_call in message.tool_calls
                ]
            elif message.tool_name and message.tool_call_id:
                try:
                    arguments = json.loads(message.content) if message.content else {}
                except json.JSONDecodeError:
                    arguments = {}
                entry["content"] = None
                entry["tool_calls"] = [{
                    "id"       : message.tool_call_id,
                    "type"     : "function",
                    "function" : {
                        "name"      : message.tool_name,
                        "arguments" : json.dumps(arguments),
                    },
                }]
            openai_messages.append(entry)
        else:
            openai_messages.append({
                "role"    : message.role,
                "content" : message.content,
            })
    return openai_messages


class OpenAiCompatibleProvider:
    _api_key  : str
    _base_url : str
    _model    : str

    def __init__(
        self,
        api_key  : str = "",
        base_url : str = "",
        model    : str = "",
        **_kwargs : Any,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required for OpenAI-compatible providers")
        if not model:
            raise ValueError("model is required for OpenAI-compatible providers")
        self._api_key  = api_key
        self._base_url = base_url
        self._model    = model

    def chat(
        self,
        messages : list[ChatMessage],
        tools    : list[ToolSpec],
    ) -> Iterator[ChatEvent]:
        if not messages:
            yield ChatEvent(ChatEventType.DONE)
            return

        client = OpenAI(
            api_key  = self._api_key or "unused",
            base_url = self._base_url,
        )

        try:
            create_kwargs : dict[str, Any] = {
                "model"    : self._model,
                "messages" : _toOpenaiMessages(messages),
                "stream"   : True,
            }
            tool_defs = _toolDefinitions(tools)
            if tool_defs:
                create_kwargs["tools"] = tool_defs
            stream = client.chat.completions.create(**create_kwargs)
        except Exception as exc:
            yield ChatEvent(ChatEventType.ERROR, error=str(exc))
            yield ChatEvent(ChatEventType.DONE)
            return

        tool_calls : dict[int, dict[str, str]] = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta  = choice.delta

            if delta.content:
                yield ChatEvent(ChatEventType.TOKEN, delta.content)

            if delta.tool_calls:
                for part in delta.tool_calls:
                    index = part.index or 0
                    entry = tool_calls.setdefault(
                        index,
                        {"id" : "", "name" : "", "arguments" : ""},
                    )
                    if part.id:
                        entry["id"] = part.id
                    if part.function:
                        if part.function.name:
                            entry["name"] = part.function.name
                        if part.function.arguments:
                            entry["arguments"] += part.function.arguments

        for entry in tool_calls.values():
            if not entry["name"]:
                continue
            try:
                arguments = json.loads(entry["arguments"] or "{}")
            except json.JSONDecodeError:
                arguments = {}
            yield ChatEvent(
                ChatEventType.TOOL_CALL,
                tool_call = ToolCall(
                    id        = entry["id"] or entry["name"],
                    name      = entry["name"],
                    arguments = arguments,
                ),
            )

        yield ChatEvent(ChatEventType.DONE)
