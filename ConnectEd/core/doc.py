import os

from typing          import Self, Protocol
from dataclasses     import dataclass
from abc             import ABC, abstractmethod

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QIcon

from ..app import logger, session, window

from ..core.xml import saveXml

from .check import checked


class DocSubjectProtocol(Protocol):
    def name(self : Self) -> str:
        ...


@dataclass
class NavItemSpec:
    subject  : str | DocSubjectProtocol
    icon     : QIcon | None = None
    tip      : str | None = None
    children : list["NavItemSpec"] | None = None


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
        saveXml(self, path)

    @classmethod
    @abstractmethod
    def load(cls : type[Self], path : str) -> bool:
        if not os.path.exists(path):
            logger().warning(f"{path} not found")
            return False
        xr = QXmlStreamReader(path)
        return self.fromXml(xr)

    # --- Navigator tree -------------------------------------------------------

    @abstractmethod
    def navItemSpec(self : Self) -> NavItemSpec:
        """Specifies navigator row (and any child rows)."""
        ...

    @abstractmethod
    def navOpen(self : Self, widget : DocSubjectProtocol) -> None:
        """Open an editor window for the specified widget."""
        ...

    @abstractmethod
    def navRename(self : Self, widget : DocSubjectProtocol, name : str) -> None:
        """Rename the specified widget."""
        ...

    # TODO: remove this?
    @checked
    def navigatorItem(self : Self, child_id : str) -> NavItemSpec | None:
        """Look up one child row by id."""
        for item in self.navItemSpec():
            if item.id == child_id:
                return item
        return None

    # TODO: remove this?
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

    @abstractmethod
    def windowTitle(self : Self, subject : DocSubjectProtocol) -> str:
        ...


@dataclass
class DocBinding:
    doc     : Doc
    subject : DocSubjectProtocol
