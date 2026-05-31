"""Unit tests for the AI GUI driver."""

from ConnectEd.ai.driver import AiDriver


def test_ping_returns_client_identity() -> None:
    driver = AiDriver.__new__(AiDriver)
    assert driver.ping() == "ConnectEd AI chat client"
