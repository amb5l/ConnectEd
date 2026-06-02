"""Unit tests for AI chat HTML helpers."""

from ConnectEd.ai.html import escape, linkify, userMessageHtml


def test_escape_prevents_html_injection() -> None:
    assert escape("<script>") == "&lt;script&gt;"


def test_user_message_html_uses_rounded_bubble() -> None:
    html_block = userMessageHtml("Hello", "#3a3a3a")
    assert "border-radius: 10px" in html_block
    assert "background-color: #3a3a3a" in html_block
    assert "Hello" in html_block
    assert "You:" not in html_block


def test_user_message_html_escapes_markup() -> None:
    html_block = userMessageHtml("<tag>", "#222222")
    assert "&lt;tag&gt;" in html_block


def test_user_message_html_preserves_line_breaks() -> None:
    html_block = userMessageHtml("line one\nline two", "#222222")
    assert "line one<br>line two" in html_block


def test_linkify_wraps_https_urls() -> None:
    result = linkify("See https://ollama.com/ for details.")
    assert '<a href="https://ollama.com/">https://ollama.com/</a>' in result
    assert "<script>" not in result
