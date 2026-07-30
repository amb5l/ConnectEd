from typing import Self

from PyQt6.QtWidgets import QSplitter

from ...core.check import checked

from ...domains.hdl.schematic.library import HdlSchematicLibrary

from .defaults    import LibraryDefaultsPane
from .list        import LibraryListPane
from .preview     import LibraryPreviewPane
from .sub_window  import LibrarySubWindow


class LibraryBrowser(QSplitter):
    # instance attributes
    _library     : HdlSchematicLibrary
    _defaults    : LibraryDefaultsPane
    _list        : LibraryListPane
    _preview     : LibraryPreviewPane

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibrarySubWindow | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._defaults = LibraryDefaultsPane(library, self)
        self._list = LibraryListPane(library, self)
        self._preview = LibraryPreviewPane(library, self)
        self.addWidget(self._defaults)
        self.addWidget(self._list)
        self.addWidget(self._preview)
        self._list.selectionChanged.connect(self._preview.setDefinition)
