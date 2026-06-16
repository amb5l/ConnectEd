import os

from typing          import Self
from dataclasses     import dataclass
from abc             import ABC, abstractmethod
from collections.abc import Callable

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QWidget

from ..app import logger, session, window

from .check import checked
from .xml   import saveBegin, saveEnd


@dataclass
class NavItemSpec:
    """
    Supports specification of a document's child rows.

    ``id`` is stable within the owning document; Navigator passes it to
    ``openChild`` / rename hooks. ``kind`` selects context-menu specs together
    with the document's ``DocType.tag``.
    """

    id          : str
    label       : str
    kind        : str
    editable    : bool = True
    open        : Callable[[str], None] | None      # None => container row
    label       : str | Callable[[], str]           # Callable => dynamic label
    child_specs : list["NavItemSpec"] | None = None


class Doc(ABC):
    """
    Session-owned document.

    Persistence methods are used by ``Session``; Navigator methods keep
    ``Navigator`` / ``NavigatorModel`` document-agnostic. Concrete classes live
    under ``ConnectEd.documents`` (e.g. ``SchematicDoc``, ``LibraryDoc``).
    """

    def onChanged(self : Self) -> None:
        session().onDocChanged(self)

    # --- persistence (Session) ------------------------------------------------

    @abstractmethod
    def path(self : Self) -> str:
        """Filesystem path, or ``\"\"`` if unsaved."""

    @abstractmethod
    def setPath(self : Self, path : str) -> None:
        ...

    @abstractmethod
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        ...

    @classmethod
    @abstractmethod
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        ...

    @checked
    def save(self : Self, path : str | None = None) -> bool:
        if path is None:
            path = self.path()
        else:
            self.setPath(path)
        if path == "":
            logger().warning(f"Document has no path to save to: {self}")
            return False
        xw, file = saveBegin(path)
        self.toXml(xw)
        saveEnd(xw, file)
        return True

    def load(self : Self, path : str) -> bool:
        if not os.path.exists(path):
            logger().warning(f"{path} not found")
            return False
        xr = QXmlStreamReader(path)
        return self.fromXml(xr)

    # --- display (Navigator tree, MDI title prefix) ---------------------------

    def displayName(self : Self) -> str:
        return self._display_name

    # --- Navigator tree -------------------------------------------------------

    @abstractmethod
    def navChildSpecs(self : Self) -> list[NavItemSpec]:
        """Child rows shown under this document in the Navigator."""
        ...

    @checked
    def navigatorItem(self : Self, child_id : str) -> NavItemSpec | None:
        """Look up one child row by id."""
        for item in self.navChildSpecs():
            if item.id == child_id:
                return item
        return None

    @checked
    def renameNavigatorChild(self : Self, child_id : str, label : str) -> None:
        """Rename a child row (e.g. symbol name). Override when ``editable``."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support renaming child {child_id!r}"
        )

    # --- Navigator UI ---------------------------------------------------------

    @abstractmethod
    def open(self : Self, widget : QWidget) -> None:
        scene = node.scene()
        # get existing subwindows in top down Z order
        subwindows = window().mdiArea().sceneSubWindows(scene)
        if subwindows:
            # bring existing window to front
            window().mdiArea().activateSubWindow(subwindows[0])
        else:
            # create a new window
            self._newDrawingWindow(node)
    # --- open / edit (Navigator, MDI) -----------------------------------------

    @abstractmethod
    def openDefault(self : Self) -> None:
        """
        Open or focus the primary editor for this document
        (e.g. schematic diagram, library container).
        """

    @checked
    def openChild(self : Self, child_id : str) -> None:
        """
        Open or focus an editor for one Navigator child row
        (e.g. symbol definition in a library).
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support openChild({child_id!r})"
        )

    # --- window management ----------------------------------------------------

    @abstractmethod
    def newWindow(self : Self, widget : QWidget) -> None:
        ...


@dataclass
class DocBinding:
    doc    : Doc
    widget : QWidget | None  # e.g. DiagramScene, SymbolItem
