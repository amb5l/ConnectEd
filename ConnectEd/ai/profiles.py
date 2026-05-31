"""Configured AI profiles and provider presets."""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Self

from ..app import settings
from ..core.check import checked

_ENV_REF = re.compile(r"^\$[A-Za-z_][A-Za-z0-9_]*$")

_PROVIDER_SHORT_NAMES : dict[str, str] = {
    "xai"              : "xAI",
    "anthropic"        : "Anthropic",
    "openai"           : "OpenAI",
    "ollama"           : "Ollama",
    "openai_compatible": "OpenAI-compatible",
}


@dataclass(frozen=True)
class ProviderPreset:
    label        : str
    provider     : str
    api_key_name : str
    api_key_value: str
    url          : str


PROVIDER_PRESETS : tuple[ProviderPreset, ...] = (
    ProviderPreset(
        label         = "Grok (xAI)",
        provider      = "xai",
        api_key_name  = "$XAI_API_KEY",
        api_key_value = "",
        url           = "https://api.x.ai/v1",
    ),
    ProviderPreset(
        label         = "Claude (Anthropic)",
        provider      = "anthropic",
        api_key_name  = "$ANTHROPIC_API_KEY",
        api_key_value = "",
        url           = "",
    ),
    ProviderPreset(
        label         = "GPT (OpenAI)",
        provider      = "openai",
        api_key_name  = "$OPENAI_API_KEY",
        api_key_value = "",
        url           = "https://api.openai.com/v1",
    ),
    ProviderPreset(
        label         = "Ollama (local)",
        provider      = "ollama",
        api_key_name  = "",
        api_key_value = "",
        url           = "http://localhost:11434/v1",
    ),
    ProviderPreset(
        label         = "OpenAI-compatible",
        provider      = "openai_compatible",
        api_key_name  = "$OPENAI_API_KEY",
        api_key_value = "",
        url           = "",
    ),
)

_PRESET_LABELS : dict[str, str] = {p.provider : p.label for p in PROVIDER_PRESETS}


@dataclass
class AiProfile:
    id            : str
    provider      : str
    api_key_name  : str
    api_key_value : str
    url           : str
    cached_models : list[str] = field(default_factory=list)

    @classmethod
    def fromPreset(cls : type[Self], preset : ProviderPreset) -> Self:
        return cls(
            id            = uuid.uuid4().hex,
            provider      = preset.provider,
            api_key_name  = preset.api_key_name,
            api_key_value = preset.api_key_value,
            url           = preset.url,
        )

    @classmethod
    def fromDict(cls : type[Self], data : dict) -> Self:
        api_key_name, api_key_value = _keyFieldsFromDict(data)
        url = str(data.get("url", data.get("base_url", "")))
        cached = data.get("cached_models", [])
        if not isinstance(cached, list):
            cached = []
        return cls(
            id            = str(data.get("id", uuid.uuid4().hex)),
            provider      = str(data.get("provider", "")),
            api_key_name  = api_key_name,
            api_key_value = api_key_value,
            url           = url,
            cached_models = [str(model) for model in cached],
        )

    def toDict(self : Self) -> dict[str, Any]:
        return asdict(self)

    def displayLabel(self : Self) -> str:
        return profileMenuLabel(self)

    def chatLabel(self : Self) -> str:
        """Short label for dock titles (provider/key only)."""
        return profileMenuLabel(self)

    def resolvedUrl(self : Self) -> str:
        if self.url.strip():
            return self.url.strip()
        preset = presetForProvider(self.provider)
        return preset.url if preset is not None else ""

    def resolvedBaseUrl(self : Self) -> str:
        return self.resolvedUrl()


def providerShortName(provider : str) -> str:
    if not provider:
        return "no provider"
    return _PROVIDER_SHORT_NAMES.get(provider, provider)


def profileMenuLabel(profile : AiProfile) -> str:
    key = profileKeyLabel(profile.api_key_name)
    return f"{providerShortName(profile.provider)}/{key}"


def connectionLabel(profile : AiProfile, model : str) -> str:
    return f"{connectionPrefix(profile)}:{model}"


def connectionPrefix(profile : AiProfile) -> str:
    return (
        f"{providerShortName(profile.provider)}:"
        f"{profileKeyLabel(profile.api_key_name)}"
    )


def profileKeyLabel(api_key_name : str) -> str:
    name = api_key_name.strip()
    if not name:
        return "?"
    if name.startswith("$"):
        return name[1:]
    return name


def isEnvKeyName(api_key_name : str) -> bool:
    return api_key_name.strip().startswith("$")


def envVarName(api_key_name : str) -> str:
    name = api_key_name.strip()
    if name.startswith("$"):
        return name[1:]
    return name


def envKeyDisplayText(api_key_name : str) -> tuple[str, bool]:
    """Return display text and whether the env var is missing (undefined)."""
    if not isEnvKeyName(api_key_name):
        return "", False
    env_name = envVarName(api_key_name)
    value = os.environ.get(env_name, "")
    if value:
        return value, False
    return f"{env_name} undefined", True


def _normalizeApiKeyName(name : str) -> str:
    name = name.strip()
    if not name or name.startswith("$"):
        return name
    if _ENV_REF.match(f"${name}"):
        return f"${name}"
    return name


def _keyFieldsFromDict(data : dict) -> tuple[str, str]:
    if "api_key_name" in data or "api_key_value" in data:
        api_key_name  = _normalizeApiKeyName(str(data.get("api_key_name", "")))
        api_key_value = str(data.get("api_key_value", ""))
        if api_key_value and _ENV_REF.match(api_key_value):
            if not api_key_name:
                api_key_name = api_key_value
            api_key_value = ""
        return api_key_name, api_key_value
    old = str(data.get("api_key", ""))
    if old.startswith("$"):
        return old, ""
    return "", old


def providerPresetLabel(provider : str) -> str:
    if not provider:
        return "no provider"
    return _PRESET_LABELS.get(provider, provider)


def presetForProvider(provider : str) -> ProviderPreset | None:
    for preset in PROVIDER_PRESETS:
        if preset.provider == provider:
            return preset
    return None


def resolveApiKey(profile : AiProfile) -> str:
    """Resolve the secret for a profile (``$ENV`` key name or literal value)."""
    name = profile.api_key_name.strip()
    if isEnvKeyName(name):
        return os.environ.get(envVarName(name), "")
    value = profile.api_key_value.strip()
    if value:
        if _ENV_REF.match(value):
            return os.environ.get(value[1:], "")
        return value
    if name:
        return os.environ.get(name, "")
    return ""


def defaultProfilesJson() -> str:
    profiles = [AiProfile.fromPreset(p) for p in PROVIDER_PRESETS[:4]]
    return json.dumps([p.toDict() for p in profiles])


@checked
def loadProfiles() -> list[AiProfile]:
    raw = settings().get("ai/profiles_data") or "[]"
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(items, list):
        return []
    return [AiProfile.fromDict(item) for item in items if isinstance(item, dict)]


@checked
def saveProfiles(profiles : list[AiProfile]) -> None:
    settings().set(
        "ai/profiles_data",
        json.dumps([p.toDict() for p in profiles]),
        emit = False,
    )
    if profiles:
        default_id = settings().get("ai/default_profile")
        if not default_id or not profileById(profiles, default_id):
            settings().set("ai/default_profile", profiles[0].id, emit=False)
    else:
        settings().set("ai/default_profile", "", emit=False)


def profileById(profiles : list[AiProfile], profile_id : str) -> AiProfile | None:
    for profile in profiles:
        if profile.id == profile_id:
            return profile
    return None


@checked
def getProfile(profile_id : str | None = None) -> AiProfile | None:
    profiles = loadProfiles()
    if not profiles:
        return None
    if profile_id:
        found = profileById(profiles, profile_id)
        if found is not None:
            return found
    default_id = settings().get("ai/default_profile")
    if default_id:
        found = profileById(profiles, default_id)
        if found is not None:
            return found
    return profiles[0]
