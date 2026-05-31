"""Shared types for the AI chat agent loop."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChatEventType(Enum):
    TOKEN     = "token"
    TOOL_CALL = "tool_call"
    DONE      = "done"
    ERROR     = "error"


@dataclass
class ChatMessage:
    role         : str
    content      : str
    tool_call_id : str | None = None
    tool_name    : str | None = None
    tool_calls   : list[ToolCall] | None = None


@dataclass
class ToolDefinition:
    name        : str
    description : str
    parameters  : dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    id        : str
    name      : str
    arguments : dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatEvent:
    type      : ChatEventType
    content   : str            = ""
    tool_call : ToolCall | None = None
    error     : str | None     = None
