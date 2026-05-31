"""Unit tests for AI model profiles and env key resolution."""

import json

import pytest
from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.profiles import (
    AiProfile,
    ProviderPreset,
    defaultProfilesJson,
    envKeyDisplayText,
    isEnvKeyName,
    loadProfiles,
    profileMenuLabel,
    providerPresetLabel,
    resolveApiKey,
    saveProfiles,
)
from ConnectEd.core.settings import Settings


@pytest.fixture
def settings_store(monkeypatch : pytest.MonkeyPatch):
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    store = Settings()
    monkeypatch.setattr("ConnectEd.app.settings", lambda: store)
    monkeypatch.setattr("ConnectEd.ai.profiles.settings", lambda: store)
    return store


def test_provider_preset_labels() -> None:
    assert providerPresetLabel("") == "no provider"
    assert providerPresetLabel("xai") == "Grok (xAI)"
    assert providerPresetLabel("anthropic") == "Claude (Anthropic)"
    assert providerPresetLabel("openai") == "GPT (OpenAI)"
    assert providerPresetLabel("ollama") == "Ollama (local)"
    assert providerPresetLabel("custom") == "custom"


def test_is_env_key_name() -> None:
    assert isEnvKeyName("$XAI_API_KEY")
    assert not isEnvKeyName("ConnectEdDev")
    assert not isEnvKeyName("")


def test_env_key_display_text(monkeypatch : pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "secret")
    text, italic = envKeyDisplayText("$XAI_API_KEY")
    assert text == "secret"
    assert italic is False

    monkeypatch.delenv("MISSING_KEY", raising=False)
    text, italic = envKeyDisplayText("$MISSING_KEY")
    assert text == "MISSING_KEY undefined"
    assert italic is True


def test_profile_menu_label() -> None:
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "ConnectEdDev",
        api_key_value = "",
        url           = "",
    )
    assert profileMenuLabel(profile) == "xAI/ConnectEdDev"

    env_profile = AiProfile(
        id            = "2",
        provider      = "xai",
        api_key_name  = "$XAI_API_KEY",
        api_key_value = "",
        url           = "",
    )
    assert profileMenuLabel(env_profile) == "xAI/XAI_API_KEY"


def test_resolve_api_key_from_env_name(monkeypatch : pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "secret")
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "$XAI_API_KEY",
        api_key_value = "",
        url           = "",
    )
    assert resolveApiKey(profile) == "secret"


def test_resolve_api_key_literal_value() -> None:
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "ConnectEdDev",
        api_key_value = "xai-live-key",
        url           = "",
    )
    assert resolveApiKey(profile) == "xai-live-key"


def test_resolve_api_key_dollar_env_in_value_legacy(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    profile = AiProfile(
        id            = "1",
        provider      = "openai",
        api_key_name  = "",
        api_key_value = "$OPENAI_API_KEY",
        url           = "",
    )
    assert resolveApiKey(profile) == "sk-test"


def test_profile_from_preset() -> None:
    preset = ProviderPreset(
        label         = "Grok (xAI)",
        provider      = "xai",
        api_key_name  = "$XAI_API_KEY",
        api_key_value = "",
        url           = "https://api.x.ai/v1",
    )
    profile = AiProfile.fromPreset(preset)
    assert profile.provider == "xai"
    assert profile.api_key_name == "$XAI_API_KEY"
    assert profile.url == "https://api.x.ai/v1"


def test_from_dict_migrates_legacy_fields() -> None:
    profile = AiProfile.fromDict({
        "id"       : "1",
        "provider" : "xai",
        "api_key"  : "$XAI_API_KEY",
        "base_url" : "https://api.x.ai/v1",
        "cached_models" : ["grok-3", "grok-2"],
    })
    assert profile.api_key_name == "$XAI_API_KEY"
    assert profile.api_key_value == ""
    assert profile.url == "https://api.x.ai/v1"
    assert profile.cached_models == ["grok-3", "grok-2"]


def test_from_dict_migrates_bare_env_name() -> None:
    profile = AiProfile.fromDict({
        "id"           : "1",
        "provider"     : "xai",
        "api_key_name" : "XAI_API_KEY",
        "api_key_value": "",
    })
    assert profile.api_key_name == "$XAI_API_KEY"


def test_save_and_load_profiles(settings_store : Settings) -> None:
    profiles = [
        AiProfile(
            id            = "a",
            provider      = "xai",
            api_key_name  = "$XAI_API_KEY",
            api_key_value = "",
            url           = "https://api.x.ai/v1",
            cached_models = ["grok-3"],
        )
    ]
    saveProfiles(profiles)
    loaded = loadProfiles()
    assert len(loaded) == 1
    assert loaded[0].provider == "xai"
    assert loaded[0].api_key_name == "$XAI_API_KEY"
    assert loaded[0].cached_models == ["grok-3"]
    from ConnectEd.app import settings
    assert settings().get("ai/default_profile") == "a"


def test_default_profiles_json_is_valid() -> None:
    items = json.loads(defaultProfilesJson())
    assert len(items) == 4
    assert items[0]["provider"] == "xai"
    assert items[0]["api_key_name"] == "$XAI_API_KEY"
    assert "model" not in items[0]
