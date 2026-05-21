"""Unit tests for AI chat HTML helpers."""

from ConnectEd.ai.html import escape, linkify


def test_escape_prevents_html_injection() -> None:
    assert escape("<script>") == "&lt;script&gt;"


def test_linkify_wraps_https_urls() -> None:
    result = linkify("See https://ollama.com/ for details.")
    assert '<a href="https://ollama.com/">https://ollama.com/</a>' in result
    assert "<script>" not in result
