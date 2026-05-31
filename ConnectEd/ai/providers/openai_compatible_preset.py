"""OpenAI-compatible preset — user-supplied base URL."""

from __future__ import annotations

from typing import Any

from .openai_compatible import OpenAiCompatibleProvider, listModels as _listModels

DEFAULT_API_KEY_NAME = "$OPENAI_API_KEY"


class OpenAiCompatiblePresetProvider(OpenAiCompatibleProvider):
    """Registered as ``openai_compatible``; requires explicit base_url and model."""

    def __init__(
        self,
        api_key  : str = "",
        base_url : str = "",
        model    : str = "",
        **_kwargs : Any,
    ) -> None:
        super().__init__(
            api_key  = api_key,
            base_url = base_url,
            model    = model,
        )


def listModels(api_key : str, base_url : str = "") -> list[str]:
    return _listModels(api_key, base_url)
