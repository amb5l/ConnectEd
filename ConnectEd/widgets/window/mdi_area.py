import os

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiArea, QWidget
from PyQt6.QtGui     import QAction

from ...app import window

from ...core.check import checked
from ...core.doc   import Doc, DocSubjectProtocol

from ..action import Action

from .sub_window  import DocSubWindow


class MdiArea(QMdiArea):
    _mru     : list[DocSubWindow]
    _actions : dict[Doc, dict[DocSubjectProtocol, list[Action]]]

    @checked
    def __init__(self : Self) -> None:
        super().__init__()
        self._mru = []
        self._actions = {}
        self.subWindowActivated.connect(self._touchMRU)

    def onSubWindowsChanged(self : Self) -> None:
        # build tree of subwindows by doc and subject
        tree : dict[Doc, dict[DocSubjectProtocol, list[DocSubWindow]]] = {}
        for subwindow in self.subWindowList():
            if not isinstance(subwindow, DocSubWindow):
                continue
            binding = subwindow.docBinding()
            if binding is None:
                continue
            doc = binding.doc
            subject = binding.subject
            tree.setdefault(doc, {})
            tree[doc].setdefault(subject, []).append(subwindow)
        # update titles and actions
        # (sort docs by path basename; sort subjects by window title)
        def _doc_key(doc : Doc) -> tuple[bool, str, str]:
            path = doc.path()
            return (
                path == "",
                os.path.basename(path).casefold() if path else "",
                path.casefold()
            )
        def _subject_key(
            doc     : Doc,
            subject : DocSubjectProtocol,
        ) -> str:
            return doc.windowTitle(subject).casefold()
        actions : dict[Doc, dict[DocSubjectProtocol, list[Action]]] = {}
        for doc in sorted(tree, key=_doc_key):
            subjects = tree[doc]
            for subject in sorted(subjects, key=lambda s: _subject_key(doc, s)):
                subwindows = subjects[subject]
                title = doc.windowTitle(subject)
                for i, subwindow in enumerate(subwindows):
                    suffix = f" ({i + 1})" if len(subwindows) > 1 else ""
                    subwindow.setWindowTitle(title + suffix)
                    action = QAction(window())
                    action.setText(title + suffix)
                    action.triggered.connect(
                        lambda checked=False, window=subwindow:
                            self.activateSubWindow(window)
                    )
                    actions.setdefault(doc, {})
                    actions[doc].setdefault(subject, []).append(action)
        self._actions = actions
        # propagate changes to menu bar
        window().menuBar().updateWindowMenu()

    def mruSubWindows(self) -> list[DocSubWindow]:
        return list(self._mru)

    def preferredSubWindow(self, doc, subject) -> DocSubWindow | None:
        for w in self.mruSubWindows():
            b = w.docBinding()
            if b and b.doc is doc and b.subject is subject:
                return w
        return None

    @checked
    def addSubWindow(
        self      : Self,
        subwindow : QWidget,
        flags     : Qt.WindowType = Qt.WindowType.SubWindow
    ) -> None:
        super().addSubWindow(subwindow, flags)
        if isinstance(subwindow, DocSubWindow):
            subwindow.destroyed.connect(
                lambda *, w=subwindow: self._removeFromMru(w)
            )
            self._mru.append(subwindow)
        self.onSubWindowsChanged()

    def nextSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(1)

    def previousSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(-1)

    @checked
    def activateSubWindow(self : Self, subwindow : DocSubWindow) -> None:
        super().setActiveSubWindow(subwindow)
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()

    def subWindowActions(
        self : Self
    ) -> dict[Doc, dict[DocSubjectProtocol, list[Action]]]:
        return self._actions

    def _activateSubWindowIndexOffset(self : Self, offset : int) -> None:
        windows = self.subWindowList()
        if not windows:
            return
        current_window = self.activeSubWindow()
        if not current_window:
            self.setActiveSubWindow(windows[0])
            return
        current_index = windows.index(current_window)
        next_index = (current_index + offset) % len(windows)
        next_window = windows[next_index]
        self.activateSubWindow(next_window)

    def _touchMRU(self : Self, subwindow : DocSubWindow | None = None) -> None:
        if not isinstance(subwindow, DocSubWindow):
            return
        try:
            self._mru.remove(subwindow)
        except ValueError:
            pass
        self._mru.insert(0, subwindow)

    def _removeFromMru(self : Self, subwindow : DocSubWindow) -> None:
        try:
            self._mru.remove(subwindow)
        except ValueError:
            pass
        self.onSubWindowsChanged()
