"""Pluggable LLM backend registry."""

from typing import Any

_providers : dict[str, type] = {}


def register_provider(name : str, cls : type) -> None:
    _providers[name] = cls


def list_providers() -> list[str]:
    return list(_providers.keys())


def providerDisplayLabel(provider_key : str) -> str:
    if provider_key and provider_key != "dummy":
        return provider_key
    return "no provider"


def create_provider(name : str, **kwargs : Any):
    if name not in _providers:
        raise KeyError(f"Unknown AI provider: {name!r}")
    return _providers[name](**kwargs)


# Register built-in providers.
from . import dummy  # noqa: E402, F401

register_provider("dummy", dummy.DummyProvider)
