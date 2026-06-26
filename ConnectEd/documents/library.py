from __future__ import annotations

from ..core.session import DocType, Session
from ..core.doc     import Doc


class HdlSchematicLibraryDoc(Doc):
    _XML_TAG = "HdlSchematicLibrary"


DOC_TYPE = DocType(
    name  = "HDL Schematic Library",
    group = "HDL Schematic Libraries",
    ext   = "hdl_lib",
    cls   = HdlSchematicLibraryDoc,
)

Session.registerDocType(DOC_TYPE)
