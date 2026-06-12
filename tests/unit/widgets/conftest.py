"""Pytest hooks for widget unit tests."""

from __future__ import annotations

import pytest


def pytest_addoption(parser : pytest.Parser) -> None:
    parser.addoption(
        "--save-dsn",
        action  = "store",
        default = None,
        metavar = "PATH",
        help    = (
            "After building the text permutation matrix, save the design to PATH "
            "(for viewing in ConnectEd; not required for CI)"
        ),
    )
