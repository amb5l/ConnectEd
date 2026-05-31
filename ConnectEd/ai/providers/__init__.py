"""Pluggable LLM backend registry."""

from __future__ import annotations

from typing import Any

from ..profiles import AiProfile, providerPresetLabel, resolveApiKey

_providers : dict[str, type] = {}


def registerProvider(name : str, cls : type) -> None:
    _providers[name] = cls


def listProviders() -> list[str]:
    return list(_providers.keys())


def providerDisplayLabel(provider_key : str) -> str:
    return providerPresetLabel(provider_key)


def createProvider(name : str, **kwargs : Any):
    if name not in _providers:
        raise KeyError(f"Unknown AI provider: {name!r}")
    return _providers[name](**kwargs)


def createProviderForProfile(profile : AiProfile | None, model : str = ""):
    if profile is None or not profile.provider:
        raise ValueError("AI profile is required")
    api_key  = resolveApiKey(profile)
    base_url = profile.resolvedBaseUrl()
    model    = model.strip()
    if profile.provider != "ollama" and not api_key:
        raise ValueError(
            f"API key is required for {providerDisplayLabel(profile.provider)}"
        )
    if not model:
        raise ValueError(
            f"Model is required for {providerDisplayLabel(profile.provider)}"
        )
    return createProvider(
        profile.provider,
        api_key  = api_key,
        base_url = base_url,
        model    = model,
    )


def listModelsForProfile(profile : AiProfile) -> list[str]:
    list_fn = _LIST_MODELS.get(profile.provider)
    if list_fn is None:
        return []
    api_key  = resolveApiKey(profile)
    base_url = profile.resolvedBaseUrl()
    return list_fn(api_key, base_url)


def defaultApiKeyName(provider : str) -> str:
    return _DEFAULT_API_KEY_NAMES.get(provider, "")


def defaultBaseUrl(provider : str) -> str:
    return _DEFAULT_BASE_URLS.get(provider, "")


# Register built-in providers.
from . import (  # noqa: E402
    anthropic,
    ollama,
    openai_api,
    openai_compatible_preset,
    xai,
)

registerProvider("xai", xai.XaiProvider)
registerProvider("anthropic", anthropic.AnthropicProvider)
registerProvider("openai", openai_api.OpenAiProvider)
registerProvider("ollama", ollama.OllamaProvider)
registerProvider(
    "openai_compatible",
    openai_compatible_preset.OpenAiCompatiblePresetProvider,
)

_LIST_MODELS : dict[str, Any] = {
    "xai"              : xai.listModels,
    "openai"           : openai_api.listModels,
    "ollama"           : ollama.listModels,
    "openai_compatible": openai_compatible_preset.listModels,
    "anthropic"        : anthropic.listModels,
}

_DEFAULT_API_KEY_NAMES : dict[str, str] = {
    "xai"              : xai.DEFAULT_API_KEY_NAME,
    "openai"           : openai_api.DEFAULT_API_KEY_NAME,
    "ollama"           : ollama.DEFAULT_API_KEY_NAME,
    "openai_compatible": openai_compatible_preset.DEFAULT_API_KEY_NAME,
    "anthropic"        : anthropic.DEFAULT_API_KEY_NAME,
}

_DEFAULT_BASE_URLS : dict[str, str] = {
    "xai"              : xai.DEFAULT_BASE_URL,
    "openai"           : openai_api.DEFAULT_BASE_URL,
    "ollama"           : ollama.DEFAULT_BASE_URL,
    "openai_compatible": "",
    "anthropic"        : "",
}
