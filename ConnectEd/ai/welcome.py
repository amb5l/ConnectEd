"""Getting-started welcome shown in new AI chat docks."""

from .html import escape

_SETTINGS_LINK = "connected://ai/settings"


def settingsUrl() -> str:
    return _SETTINGS_LINK


def welcomeHtml() -> str:
    return f"""\
<p>ConnectEd AI is not connected to a model yet. To get started, choose a provider
in <a href="{_SETTINGS_LINK}">AI Settings</a>.</p>
<p><b>Local (no API key)</b></p>
<ul>
<li>Install <a href="https://ollama.com/">Ollama</a>, pull a model, then set
provider to <code>ollama</code> and base URL to
<code>http://localhost:11434</code>.</li>
</ul>
<p><b>Cloud (official APIs)</b></p>
<ul>
<li><a href="https://platform.openai.com/">OpenAI</a> — create an API key;
use provider <code>openai_compatible</code> or <code>openai</code>.</li>
<li><a href="https://console.anthropic.com/">Anthropic</a> — Claude API key;
provider <code>anthropic</code>.</li>
<li><a href="https://console.x.ai/">xAI</a> — Grok API key; provider
<code>xai</code>.</li>
</ul>
<p>Many vendors offer trial or evaluation credits — check their pricing pages when
you sign up. Paste your key and model name in
<a href="{_SETTINGS_LINK}">AI Settings</a>; it is stored locally and never logged.</p>
<p>Send <code>{escape("demo")}</code> to exercise the tool-call loop with the dummy
backend.</p>"""
