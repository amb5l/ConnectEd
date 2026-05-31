"""OpenAI API — thin wrapper around OpenAI-compatible client."""

from __future__ import annotations

from typing import Any

from .openai_compatible import OpenAiCompatibleProvider, listModels as _listModels

DEFAULT_BASE_URL     = "https://api.openai.com/v1"
DEFAULT_API_KEY_NAME = "$OPENAI_API_KEY"


class OpenAiProvider(OpenAiCompatibleProvider):
    def __init__(
        self,
        api_key  : str = "",
        base_url : str = "",
        model    : str = "",
        **_kwargs : Any,
    ) -> None:
        super().__init__(
            api_key  = api_key,
            base_url = base_url or DEFAULT_BASE_URL,
            model    = model,
        )


def listModels(api_key : str, base_url : str = "") -> list[str]:
    return _listModels(api_key, base_url or DEFAULT_BASE_URL)
