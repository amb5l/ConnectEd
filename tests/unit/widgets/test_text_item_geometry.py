"""
Parented PropertyText geometry matrix: 144×144 permutation grid on DiagramScene.

Builds the full matrix in memory, validates geometry, XML round-trip, and growth.
No committed golden .dsn — suitable for CI (~few minutes).

Optional: save a viewable design::

    pytest tests/unit/widgets/test_text_item_geometry.py --save-dsn text_permutations.dsn
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.db import DesignDbNode
from ConnectEd.core.settings import Settings

from tests.unit.widgets.text_geometry_helpers import (
    CAPTION,
    GRID,
    LONG,
    TextCase,
    TextGeometry,
    assert_geometry,
    build_design,
    case_label,
    collect_cases_from_scene,
    measure,
)

pytestmark = pytest.mark.usefixtures("connect_ed_app")


@pytest.fixture(scope="module")
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


@pytest.fixture(scope="module")
def text_matrix(
    connect_ed_app : ConnectEdApp,
    request        : pytest.FixtureRequest,
) -> tuple[DesignDbNode, list[TextCase], dict[tuple[int, int], TextGeometry]]:
    node = build_design()
    save_path = request.config.getoption("--save-dsn")
    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        node.save(str(path))

    cases = collect_cases_from_scene(node.scene())
    assert len(cases) == GRID * GRID
    reference : dict[tuple[int, int], TextGeometry] = {}
    for case in cases:
        try:
            reference[(case.row, case.col)] = assert_geometry(case.text)
        except AssertionError as exc:
            raise AssertionError(f"{case_label(case)}: {exc}") from exc
    return node, cases, reference


def test_matrix_short_geometry(
    text_matrix : tuple[DesignDbNode, list[TextCase], dict[tuple[int, int], TextGeometry]],
) -> None:
    _node, cases, reference = text_matrix
    assert len(cases) == len(reference) == GRID * GRID


def test_matrix_xml_roundtrip(
    text_matrix : tuple[DesignDbNode, list[TextCase], dict[tuple[int, int], TextGeometry]],
) -> None:
    node, _cases, reference = text_matrix
    with tempfile.NamedTemporaryFile(suffix=".dsn", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        node.save(str(tmp_path))
        reloaded = DesignDbNode.load(str(tmp_path))
        reloaded_cases = collect_cases_from_scene(reloaded.scene())
        assert len(reloaded_cases) == len(reference)

        for case in reloaded_cases:
            key = (case.row, case.col)
            try:
                after = assert_geometry(case.text)
                assert after.matches(reference[key]), case_label(case)
            except AssertionError as exc:
                raise AssertionError(f"{case_label(case)}: {exc}") from exc
    finally:
        tmp_path.unlink(missing_ok=True)


def test_matrix_caption_growth(
    text_matrix : tuple[DesignDbNode, list[TextCase], dict[tuple[int, int], TextGeometry]],
) -> None:
    _node, cases, _reference = text_matrix
    for case in cases:
        short_geom = measure(case.text)
        case.poly.properties.setValue(CAPTION, LONG)
        long_geom = assert_geometry(case.text)
        assert long_geom.text == LONG, case_label(case)
        assert long_geom.width >= short_geom.width, case_label(case)
        assert long_geom.origin_scene.x() == pytest.approx(
            short_geom.origin_scene.x(), abs=0.5
        ), case_label(case)
        assert long_geom.origin_scene.y() == pytest.approx(
            short_geom.origin_scene.y(), abs=0.5
        ), case_label(case)
