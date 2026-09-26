from typing import Self

from PyQt6.QtWidgets import QSplitter
from PyQt6.QtGui     import QShowEvent

from ...core.check                    import checked

from ...domains.hdl.schematic.library import HdlSchematicLibrary

from .properties                      import LibraryPropertiesPane
from .list                            import LibraryListPane
from .preview                         import LibraryPreviewPane
from .sub_window                      import LibrarySubWindow


class LibraryBrowser(QSplitter):
    # instance attributes
    _library     : HdlSchematicLibrary
    _properties  : LibraryPropertiesPane
    _list        : LibraryListPane
    _preview     : LibraryPreviewPane
    _sized       : bool

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibrarySubWindow | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._sized = False
        self._properties = LibraryPropertiesPane(library, self)
        self._list = LibraryListPane(library, self)
        self._preview = LibraryPreviewPane(library, self)
        self.addWidget(self._properties)
        self.addWidget(self._list)
        self.addWidget(self._preview)
        for i in range(self.count()):
            self.setStretchFactor(i, 1)
            widget = self.widget(i)
            if widget is not None:
                widget.setMinimumWidth(0)
        self._list.selectionChanged.connect(self._preview.setSymbol)

    def showEvent(self : Self, a0 : QShowEvent | None) -> None:
        super().showEvent(a0)
        if self._sized:
            return
        self._sized = True
        width = max(self.width(), 1) // self.count()
        self.setSizes([width] * self.count())
