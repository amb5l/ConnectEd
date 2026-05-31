"""Fetch and cache model lists for AI profiles."""

from __future__ import annotations

from .profiles import AiProfile
from .providers import listModelsForProfile


def refreshProfileModels(profile : AiProfile) -> list[str]:
    try:
        profile.cached_models = listModelsForProfile(profile)
    except Exception:
        profile.cached_models = []
    return profile.cached_models


def refreshAllProfileModels(profiles : list[AiProfile]) -> None:
    for profile in profiles:
        refreshProfileModels(profile)


def anyProfileMissingModels(profiles : list[AiProfile]) -> bool:
    return any(not profile.cached_models for profile in profiles)
