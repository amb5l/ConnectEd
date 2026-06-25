from typing      import Self, Protocol
from dataclasses import dataclass
from abc         import ABC, abstractmethod

from PyQt6.QtCore import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QIcon

from ..app import session

from ..core.types import MenuEntry, MenuAction
from ..core.xml   import saveXml

from .check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .session import DocType
    from ..widgets.window.navigator import Navigator
    from ..widgets.window.sub_window import DocSubWindow


@dataclass
class NavItemSpec:
    subject  : str | "DocSubjectProtocol"
    icon     : QIcon | None = None
    tip      : str | None = None
    children : list["NavItemSpec"] | None = None


class DocSubjectProtocol(Protocol):
    def name(self : Self) -> str:
        ...


class Doc(ABC):
    """
    Session-owned document.

    Persistence methods are used by ``Session``; ``nav*`` and ``win*`` methods
    keep ``Navigator`` / MDI document-agnostic. Concrete classes live under
    ``ConnectEd.documents`` (e.g. ``HdlSchematicDiagramDoc``).
    """

    _XML_TAG : str

    def onChanged(self : Self) -> None:
        session().onDocChanged(self)

    # --- persistence (Session) ------------------------------------------------

    @abstractmethod
    def isClean(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> bool:
        """
        Clean state for save/close, navigator labels and window titles.

        Return ``True`` when there are no unsaved edits.
        ``subject=None`` → document-level; otherwise that bound row.
        """
        ...

    @classmethod
    def tag(cls : type[Self]) -> str:
        return cls._XML_TAG

    @abstractmethod
    def name(self : Self) -> str:
        ...

    @abstractmethod
    def setName(self : Self, name : str) -> None:
        ...

    @abstractmethod
    def path(self : Self) -> str:
        """Filesystem path, or ``\"\"`` if unsaved."""

    @abstractmethod
    def setPath(self : Self, path : str) -> None:
        """Set filesystem path; call ``onChanged()`` when the path changes."""
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
        return saveXml(self, path)

    @classmethod
    @abstractmethod
    def load(cls : type[Self], path : str) -> Self | None:
        """Load from file; return document or ``None``."""
        ...

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
    def navDisplayLabel(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str:
        """Navigator row display label; ``subject=None`` → primary subject."""
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
    ) -> list[MenuEntry]:
        """Context-menu entries; Navigator builds ``QMenu``."""
        ...

    @classmethod
    def navGroupContextMenu(
        cls      : type[Self],
        nav      : "Navigator",
        doc_type : "DocType",
    ) -> list[MenuEntry]:
        """Navigator L1 group-row menu entries for this doc type."""
        return [
            MenuAction(f"New {doc_type.name}", lambda: nav.docNew(doc_type)),
            MenuAction("Open...", lambda: nav.fileOpen(doc_type)),
        ]

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

    @abstractmethod
    def closeSubWindow(self : Self, subwindow : "DocSubWindow") -> bool:
        """Hook for cleanup/veto before a subwindow is closed."""
        ...

    @abstractmethod
    def onSubWindowClosed(self : Self, subwindow : "DocSubWindow") -> None:
        """Hook for cleanup after a subwindow is closed."""
        ...

    # --- editor lifecycle (close / save) ----------------------------------------

    @checked
    def commit(self : Self, subwindow : "DocSubWindow") -> bool:
        """Persist after edits. Override when supported."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support commit."
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
