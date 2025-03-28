import re

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiArea, QWidget

from ..views  import DrawingSubWindow, DrawingView
from ..scenes import DrawingScene


class MdiArea(QMdiArea):
    def addSubWindow(
        self   : 'MdiArea',
        widget : QWidget,
        flags  : Qt.WindowType = Qt.WindowType.SubWindow
    ) -> None:
        super().addSubWindow(widget, flags)
        if not isinstance(widget, DrawingSubWindow):
            return
        if not isinstance(widget.widget(), DrawingView):
            return
        if not isinstance(widget.widget().scene(), DrawingScene):
            return
        widget_type = type(widget.widget())
        scene = widget.widget().scene()
        scene_type = type(scene)
        sibling_subwindows = []
        for subwindow in self.subWindowList():
            if not isinstance(subwindow.widget(), widget_type):
                continue
            if not isinstance(subwindow.widget().scene(), scene_type):
                continue
            if subwindow.widget().scene() != scene:
                continue
            sibling_subwindows.append(subwindow)
        if len(sibling_subwindows) == 1:
            # remove subwindow numbering suffix
            title = sibling_subwindows[0].windowTitle()
            title = re.sub(r'\(\d+\)$', '', title).strip()
            sibling_subwindows[0].setWindowTitle(title)
        elif len(sibling_subwindows) > 1:
            for i, subwindow in enumerate(sibling_subwindows):
                title = subwindow.windowTitle()
                title = re.sub(r'\(\d+\)$', '', title).strip()
                title = f'{title} ({i + 1})'
                subwindow.setWindowTitle(title)
