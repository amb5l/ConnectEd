"""Unit tests for AI provider registry and profile wiring."""

import pytest

from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.providers import (
    createProvider,
    createProviderForProfile,
    listModelsForProfile,
)


def test_create_provider_unknown_raises() -> None:
    with pytest.raises(KeyError, match="Unknown AI provider"):
        createProvider("not-a-provider")


def test_create_provider_for_profile_none_raises() -> None:
    with pytest.raises(ValueError, match="AI profile is required"):
        createProviderForProfile(None)


def test_create_provider_for_profile_missing_key_raises() -> None:
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "",
        api_key_value = "",
        url           = "https://api.x.ai/v1",
    )
    with pytest.raises(ValueError, match="API key is required"):
        createProviderForProfile(profile, model = "grok-3")


def test_create_provider_for_profile_missing_model_raises() -> None:
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "",
        api_key_value = "secret",
        url           = "",
    )
    with pytest.raises(ValueError, match="Model is required"):
        createProviderForProfile(profile, model = "")


def test_create_provider_for_profile_xai(monkeypatch : pytest.MonkeyPatch) -> None:
    created : dict = {}

    class FakeXai:
        def __init__(self, **kwargs) -> None:
            created.update(kwargs)

    monkeypatch.setitem(
        __import__("ConnectEd.ai.providers", fromlist=["_providers"])._providers,
        "xai",
        FakeXai,
    )
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "",
        api_key_value = "secret",
        url           = "",
    )
    createProviderForProfile(profile, model = "grok-3")
    assert created["api_key"] == "secret"
    assert created["base_url"] == "https://api.x.ai/v1"
    assert created["model"] == "grok-3"


def test_list_models_for_profile_delegates(monkeypatch : pytest.MonkeyPatch) -> None:
    import ConnectEd.ai.providers as providers_module

    monkeypatch.setitem(
        providers_module._LIST_MODELS,
        "xai",
        lambda api_key, base_url: ["grok-3", "grok-2"],
    )
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "",
        api_key_value = "key",
        url           = "",
    )
    assert listModelsForProfile(profile) == ["grok-3", "grok-2"]
