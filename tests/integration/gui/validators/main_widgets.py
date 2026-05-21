"""Main window chrome: ConnectEd accessors vs Qt tree (typed chrome only)."""

from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMenuBar, QMdiArea, QStatusBar, QWidget

from ConnectEd.scripting import Window

ChromeTypes = QMenuBar | QStatusBar | QMdiArea | QDockWidget


def _findChromeWidgets(window : Window) -> list[QWidget]:
    options = Qt.FindChildOption.FindChildrenRecursively
    found : list[QWidget] = []
    for cls in (QMenuBar, QStatusBar, QMdiArea, QDockWidget):
        found.extend(
            QWidget.findChildren(window, cls, options=options)  # type: ignore[arg-type]
        )
    return found


def validateMainWidgets(
    window : Window,
    spec   : dict[str, tuple[type, Callable[[Window], Any]]],
) -> None:
    expected : list[QWidget] = []
    for name, (cls, accessor) in spec.items():
        widget : QWidget = accessor(window)
        assert widget is not None, f"{name!r} not found"
        assert isinstance(widget, cls), (
            f"{name!r}: expected {cls.__name__}, got {type(widget).__name__}"
        )
        assert widget.isVisible(), f"{name!r} not visible"
        expected.append(widget)

    found = _findChromeWidgets(window)
    for dock in found:
        if isinstance(dock, QDockWidget) and dock.isVisible():
            assert dock.windowTitle() in spec, (
                f"unexpected dock {dock.windowTitle()!r}"
            )

    assert len(found) == len(expected), (
        f"chrome count: expected {len(expected)}, found {len(found)}"
    )
    expected_ids = {id(w) for w in expected}
    found_ids = {id(w) for w in found}
    assert expected_ids == found_ids, (
        f"chrome identity mismatch: expected {len(expected_ids)}, found {len(found_ids)}"
    )
