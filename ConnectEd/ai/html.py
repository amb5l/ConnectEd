"""Safe HTML helpers for the AI chat history pane."""

import html
import re

_HTTPS_URL = re.compile(r"(https://[^\s<]+)")


def escape(text : str) -> str:
    return html.escape(text, quote=True)


def linkify(text : str) -> str:
    escaped = escape(text)
    return _HTTPS_URL.sub(r'<a href="\1">\1</a>', escaped)
