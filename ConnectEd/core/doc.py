import os

from typing          import Self, Protocol
from enum            import StrEnum
from dataclasses     import dataclass
from collections.abc import Callable
from abc             import ABC, abstractmethod

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QIcon

from ..app import logger, session

from ..core.xml import saveXml

from .check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.window.sub_window import DocSubWindow


class DocSubjectProtocol(Protocol):
    def name(self : Self) -> str:
        ...


@dataclass
class NavItemSpec:
    subject  : str | DocSubjectProtocol
    icon     : QIcon | None = None
    tip      : str | None = None
    children : list["NavItemSpec"] | None = None


class NavMenuAction(StrEnum):
    NEW        = "new"
    OPEN       = "open"
    SAVE       = "save"
    SAVE_AS    = "save_as"
    CLOSE      = "close"
    EDIT       = "edit"
    NEW_WINDOW = "new_window"
    SEPARATOR  = "separator"


@dataclass(frozen=True)
class NavMenuItem(StrEnum):
    label   : str
    handler : Callable[[], None]


class Doc(ABC):
    """
    Session-owned document.

    Persistence methods are used by ``Session``; ``nav*`` and ``win*`` methods
    keep ``Navigator`` / MDI document-agnostic. Concrete classes live under
    ``ConnectEd.documents`` (e.g. ``HdlSchematicDiagramDoc``).
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
        return cls.fromXml(xr)

    # --- Navigator (tree presentation) ----------------------------------------

    @abstractmethod
    def navItemSpec(self : Self) -> NavItemSpec:
        """Child rows under L2 (containers, symbols, …)."""
        ...

    @abstractmethod
    def navLabel(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str:
        """Navigator row label; ``subject=None`` → primary subject."""
        ...

    @abstractmethod
    def navSetLabel(
        self    : Self,
        subject : DocSubjectProtocol | None,
        label   : str,
    ) -> bool:
        """Apply inline tree edit; call ``onChanged()`` on success."""
        ...

    @abstractmethod
    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str | None:
        """Row tooltip; dynamic state — not ``NavItemSpec.tip`` alone."""
        ...

    @abstractmethod
    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> list[NavMenuAction | NavMenuItem]:
        """Context-menu entries; Navigator builds ``QMenu``."""
        ...

    # --- MDI (subwindows) -------------------------------------------------------

    @abstractmethod
    def showWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        """
        Activate existing ``(doc, subject)`` subwindow or create one.

        Returns True for success, False for failure.
        """
        ...

    @abstractmethod
    def newWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        """Always open another subwindow for the same subject (when supported)."""
        ...

    @abstractmethod
    def windowTitle(self : Self, subject : DocSubjectProtocol) -> str:
        """Subwindow / Window-menu title."""
        ...

    # --- editor lifecycle (close / save) ----------------------------------------

    @checked
    def commitEditor(self : Self, subwindow : "DocSubWindow") -> bool:
        """Persist in-editor clone (e.g. symbol Save). Override when supported."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support commitEditor"
        )

    @checked
    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        """Whether closing this editor should close the document."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support isPrimarySubject"
        )


@dataclass
class DocBinding:
    doc     : Doc
    subject : DocSubjectProtocol
