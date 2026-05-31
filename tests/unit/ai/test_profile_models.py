"""Unit tests for cached profile model lists."""

import pytest

from ConnectEd.ai.profile_models import (
    anyProfileMissingModels,
    refreshAllProfileModels,
    refreshProfileModels,
)
from ConnectEd.ai.profiles import AiProfile


def test_refresh_profile_models_stores_list(monkeypatch : pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ConnectEd.ai.profile_models.listModelsForProfile",
        lambda profile: ["grok-3", "grok-2"],
    )
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "ConnectEdDev",
        api_key_value = "key",
        url           = "",
    )
    assert refreshProfileModels(profile) == ["grok-3", "grok-2"]
    assert profile.cached_models == ["grok-3", "grok-2"]


def test_refresh_profile_models_clears_on_error(monkeypatch : pytest.MonkeyPatch) -> None:
    def _fail(_profile : AiProfile) -> list[str]:
        raise RuntimeError("network")

    monkeypatch.setattr(
        "ConnectEd.ai.profile_models.listModelsForProfile",
        _fail,
    )
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "ConnectEdDev",
        api_key_value = "key",
        url           = "",
        cached_models = ["old"],
    )
    assert refreshProfileModels(profile) == []
    assert profile.cached_models == []


def test_any_profile_missing_models() -> None:
    populated = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "key",
        api_key_value = "secret",
        url           = "",
        cached_models = ["grok-3"],
    )
    empty = AiProfile(
        id            = "2",
        provider      = "openai",
        api_key_name  = "key",
        api_key_value = "secret",
        url           = "",
        cached_models = [],
    )
    assert not anyProfileMissingModels([populated])
    assert anyProfileMissingModels([populated, empty])
    assert anyProfileMissingModels([empty])
