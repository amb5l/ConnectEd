"""Pytest hooks for widget unit tests."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

_TEXT_GEOMETRY_FILE = "test_text_item_geometry.py"
_SPARSE_COUNT       = 100
_SPARSE_SEED        = 0xC0FFEE


def pytest_addoption(parser : pytest.Parser) -> None:
    parser.addoption(
        "--full",
        action  = "store_true",
        default = False,
        help    = (
            "Run the full TextItem geometry matrix "
            f"(default: sparse, {_SPARSE_COUNT} PRNG-selected parametrized cases)"
        ),
    )


def pytest_collection_modifyitems(
    config   : pytest.Config,
    items    : list[pytest.Item],
) -> None:
    if config.getoption("--full"):
        return
    geometry = _TEXT_GEOMETRY_FILE
    candidates : list[pytest.Item] = []
    for item in items:
        if Path(str(item.path)).name != geometry:
            continue
        if "TestTextItemBaseline" in item.nodeid:
            continue
        candidates.append(item)
    if len(candidates) <= _SPARSE_COUNT:
        return
    candidates.sort(key = lambda item: item.nodeid)
    rng = random.Random(_SPARSE_SEED)
    keep = set(rng.sample(range(len(candidates)), _SPARSE_COUNT))
    for index, item in enumerate(candidates):
        if index not in keep:
            item.add_marker(
                pytest.mark.skip(
                    reason = (
                        f"sparse mode ({_SPARSE_COUNT} PRNG cases); pass --full for all"
                    )
                )
            )
