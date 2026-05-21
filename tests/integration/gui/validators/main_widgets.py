"""Main window chrome: ConnectEd accessors vs Qt tree (typed chrome only)."""

from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMenuBar, QMdiArea, QStatusBar, QWidget

from ConnectEd.scripting import AiChatDock, Window


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
    ai_chat_docks = [w for w in found if isinstance(w, AiChatDock)]
    fixed_found = [w for w in found if not isinstance(w, AiChatDock)]
    fixed_expected = [w for w in expected if not isinstance(w, AiChatDock)]

    for dock in fixed_found:
        if isinstance(dock, QDockWidget) and dock.isVisible():
            assert dock.windowTitle() in spec, (
                f"unexpected dock {dock.windowTitle()!r}"
            )

    assert len(ai_chat_docks) >= 1, "expected at least one AI chat dock"
    assert len(fixed_found) == len(fixed_expected), (
        f"chrome count: expected {len(fixed_expected)} fixed widgets, "
        f"found {len(fixed_found)}"
    )
    assert {id(w) for w in fixed_expected} == {id(w) for w in fixed_found}, (
        "fixed chrome identity mismatch"
    )
    ai_chat_widget = spec["AI Chat"][1](window)
    assert ai_chat_widget in ai_chat_docks, "AI Chat accessor not in visible docks"
