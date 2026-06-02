"""Safe HTML helpers for the AI chat history pane."""

import html
import re

_HTTPS_URL = re.compile(r"(https://[^\s<]+)")


def escape(text : str) -> str:
    return html.escape(text, quote=True)


def linkify(text : str) -> str:
    escaped = escape(text)
    return _HTTPS_URL.sub(r'<a href="\1">\1</a>', escaped)


def historyStyleSheet() -> str:
    """Layout-only CSS; font size comes from the history widget default font."""
    return """
body { margin: 0; }
p { margin-top: 0.6em; margin-bottom: 0.6em; }
pre, code { font-family: monospace; font-size: 0.9em; }
"""


def userMessageHtml(text : str, bubble_bg : str) -> str:
    """User turn as a right-aligned rounded bubble."""
    inner   = linkify(text).replace("\n", "<br>")
    padding = "8px 12px"
    radius  = "10px"
    style   = (
        f"background-color: {bubble_bg};"
        f" border-radius: {radius};"
        f" padding: {padding};"
    )
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0" '
        f'style="margin-top:0.6em;margin-bottom:0.6em;">'
        f"<tr><td align=\"right\">"
        f'<table cellpadding="0" cellspacing="0"><tr>'
        f'<td style="{style}">{inner}</td>'
        f"</tr></table></td></tr></table>"
    )
