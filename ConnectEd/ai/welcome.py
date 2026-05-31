"""Getting-started welcome shown in new AI chat docks."""

from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse

from .chat_mru import listChatMru
from .html import escape
from .profiles import connectionLabel, connectionPrefix, loadProfiles

_SETTINGS_LINK = "connected://ai/settings"


def settingsUrl() -> str:
    return _SETTINGS_LINK


def chatUrl(profile_id : str, model : str) -> str:
    query = urlencode({"profile" : profile_id, "model" : model})
    return f"connected://ai/chat?{query}"


def parseChatLink(url : str) -> tuple[str, str] | None:
    parsed = urlparse(url)
    if parsed.scheme != "connected" or parsed.netloc != "ai":
        return None
    path = parsed.path.lstrip("/")
    if path not in ("chat",):
        return None
    query = parse_qs(parsed.query)
    profile_ids = query.get("profile", [])
    models      = query.get("model", [])
    if not profile_ids or not models:
        return None
    return profile_ids[0], models[0]


def _modelLink(profile_id : str, model : str, label : str) -> str:
    href = chatUrl(profile_id, model)
    return f'<li><a href="{href}">{escape(label)}</a></li>'


def _welcomeNoProfilesHtml() -> str:
    return f"""\
<p>ConnectEd AI is not connected to a model yet. Open
<a href="{_SETTINGS_LINK}">AI Profiles</a> to add a provider and API key.</p>
<p><b>Local (no API key)</b></p>
<ul>
<li>Install <a href="https://ollama.com/">Ollama</a>, pull a model, then add an
Ollama profile with URL <code>http://localhost:11434/v1</code>.</li>
</ul>
<p><b>Cloud (official APIs)</b></p>
<ul>
<li><a href="https://platform.openai.com/">OpenAI</a></li>
<li><a href="https://console.anthropic.com/">Anthropic</a></li>
<li><a href="https://console.x.ai/">xAI</a></li>
</ul>"""


def _welcomeMruHtml(profiles : list) -> str:
    entries = listChatMru(profiles)
    if not entries:
        return ""
    links = "\n".join(
        _modelLink(profile.id, model, label)
        for profile, model, label in entries
    )
    return f"""\
<p><b>Recent</b></p>
<ul>
{links}
</ul>"""


def _welcomeAllModelsHtml(profiles : list) -> str:
    links : list[str] = []
    for profile in profiles:
        models = profile.cached_models
        if not models:
            links.append(
                f"<li>{escape(connectionPrefix(profile))} — "
                f"<i>{escape('no models cached yet')}</i></li>"
            )
            continue
        for model in models:
            links.append(
                _modelLink(
                    profile.id,
                    model,
                    connectionLabel(profile, model),
                )
            )
    if not links:
        return ""
    model_list = "\n".join(links)
    return f"""\
<p>Choose a model to start chatting in this window:</p>
<ul>
{model_list}
</ul>"""


def _welcomeConfiguredProfilesHtml() -> str:
    profiles = loadProfiles()
    blocks   = [
        _welcomeMruHtml(profiles),
        _welcomeAllModelsHtml(profiles),
    ]
    body   = "\n".join(block for block in blocks if block)
    return f"""\
{body}
<p>Manage AI API credentials in
<a href="{_SETTINGS_LINK}">AI Profiles</a>.</p>"""


def welcomeHtml() -> str:
    if loadProfiles():
        return _welcomeConfiguredProfilesHtml()
    return _welcomeNoProfilesHtml()
