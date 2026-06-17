"""GUI drawing validation: data-driven cases, fixture scenes, save/reload compare."""

from __future__ import annotations

import tempfile
from pathlib import Path

from PyQt6.QtWidgets import QMdiSubWindow

from ConnectEd.app import app, settings
from ConnectEd.core.db import DesignDbNode
from ConnectEd.scripting import Window, gui
from ConnectEd.widgets.graphics.items.rectangle import RectangleItem
from ConnectEd.widgets.graphics.views.diagram import DiagramView

from integration.gui.drawing_specs import (
    DRAWING_CASES,
    DrawingCase,
    DrawingDragStep,
    DrawingPlaceModeStep,
    DrawingStep,
)
from integration.gui.scene_compare import compare_scenes


def _active_diagram_view(driver) -> DiagramView:
    win = driver.window()
    mdi = win.mdiArea()
    assert mdi is not None
    sub = mdi.activeSubWindow()
    assert sub is not None, "no active MDI subwindow after File → New → Design"
    view = sub.widget()
    assert isinstance(view, DiagramView), (
        f"expected DiagramView, got {type(view).__name__}"
    )
    return view


def _new_design(driver, window: Window) -> None:
    connected_bar = window.menuBar()
    assert connected_bar is not None
    file_menu = connected_bar.getMenus()["File"]
    new_menu = file_menu.getSubMenus()["New"]
    design = new_menu.getAction("Design")
    assert design is not None
    design.trigger()
    driver.processEvents()
    assert app().model().designDbNodes(), "no design after File → New → Design"
    assert app().model().designDbNodes()[-1].scene() is not None


def _prepare_view(driver) -> DiagramView:
    view = _active_diagram_view(driver)
    sub = driver.window().mdiArea().activeSubWindow()
    assert isinstance(sub, QMdiSubWindow)
    driver.window().mdiArea().activateSubWindow(sub)
    view.setFocus()
    driver.processEvents()
    view.viewZoomAll()
    driver.processEvents()
    return view


def _run_step(driver, view: DiagramView, step: DrawingStep) -> None:
    if isinstance(step, DrawingPlaceModeStep):
        place = getattr(view, step.mode, None)
        assert place is not None, f"unknown place mode: {step.mode}"
        place()
        driver.processEvents()
        return
    if isinstance(step, DrawingDragStep):
        p1 = driver.viewPos(view, step.p1)
        p2 = driver.viewPos(view, step.p2)
        drag = settings().get("prefs/mouse/drag") or 5
        assert (p2 - p1).manhattanLength() > drag, (
            "mouse drag must exceed prefs/mouse/drag"
        )
        driver.mouseDrag(view, p1, p2)
        driver.processEvents()
        return
    raise TypeError(f"unsupported drawing step: {type(step)}")


def _save_and_reload(design: DesignDbNode, path: Path):
    design.save(str(path))
    reloaded = DesignDbNode.load(str(path))
    assert reloaded is not None, f"failed to reload saved design: {path}"
    return reloaded.scene()


def run_drawing_case(window: Window, case: DrawingCase) -> None:
    assert case.fixture.is_file(), f"missing fixture: {case.fixture}"
    expected = DesignDbNode.load(str(case.fixture))
    assert expected is not None, f"failed to load fixture: {case.fixture}"
    expected_scene = expected.scene()

    driver = gui(window)
    if case.new_design:
        _new_design(driver, window)
    view = _prepare_view(driver)

    for step in case.steps:
        _run_step(driver, view, step)

    scene = view.scene()
    assert scene is not None
    rectangles = [i for i in scene.items() if isinstance(i, RectangleItem)]
    assert rectangles, (
        f"expected RectangleItem on scene after drawing case {case.id!r}"
    )

    design = app().model().designDbNodes()[-1]
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".dsn", delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)
        reloaded_scene = _save_and_reload(design, tmp_path)
        compare_scenes(expected_scene, reloaded_scene)
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def validateDrawing(window: Window) -> None:
    """Run all enabled drawing cases from ``drawing_specs.DRAWING_CASES``."""
    enabled = [c for c in DRAWING_CASES if c.enabled]
    assert enabled, "no enabled drawing cases"
    for case in enabled:
        run_drawing_case(window, case)


def validateDrawingRectangle(window: Window) -> None:
    """Backward-compatible entry point (rectangle case only)."""
    validateDrawing(window)
