"""Most-recently-used AI chat connections (profile + model)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ..app import settings

from .profiles import AiProfile, connectionLabel, loadProfiles, profileById

_CHAT_MRU_MAX = 10


@dataclass
class ChatMruEntry:
    profile_id : str
    model      : str


def _loadEntries() -> list[ChatMruEntry]:
    raw = settings().get("ai/chat_mru")
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    entries : list[ChatMruEntry] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        profile_id = str(item.get("profile_id", "")).strip()
        model      = str(item.get("model", "")).strip()
        if profile_id and model:
            entries.append(ChatMruEntry(profile_id = profile_id, model = model))
    return entries


def _saveEntries(entries : list[ChatMruEntry]) -> None:
    payload = [
        {"profile_id" : entry.profile_id, "model" : entry.model}
        for entry in entries[:_CHAT_MRU_MAX]
    ]
    settings().set("ai/chat_mru", json.dumps(payload), emit = False)


def recordChatConnection(profile_id : str, model : str) -> None:
    profile_id = profile_id.strip()
    model      = model.strip()
    if not profile_id or not model:
        return
    key     = (profile_id, model)
    entries = _loadEntries()
    ordered = [ChatMruEntry(profile_id = profile_id, model = model)]
    for entry in entries:
        if (entry.profile_id, entry.model) == key:
            continue
        ordered.append(entry)
        if len(ordered) >= _CHAT_MRU_MAX:
            break
    _saveEntries(ordered)


def listChatMru(
    profiles : list[AiProfile] | None = None,
) -> list[tuple[AiProfile, str, str]]:
    """Return resolved MRU rows as (profile, model, connection_label)."""
    if profiles is None:
        profiles = loadProfiles()
    resolved : list[tuple[AiProfile, str, str]] = []
    for entry in _loadEntries():
        profile = profileById(profiles, entry.profile_id)
        if profile is None:
            continue
        resolved.append(
            (profile, entry.model, connectionLabel(profile, entry.model))
        )
    return resolved
