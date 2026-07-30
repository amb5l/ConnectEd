from __future__ import annotations

from ....core.session import DocType, Session
from ....core.doc     import Doc


class HdlFsmDiagramDoc(Doc):
    _XML_TAG = "HdlStateDiagram"


DOC_TYPE = DocType(
    name  = "HDL State Diagram",
    group = "HDL State Diagrams",
    ext   = "hdl_fsm",
    cls   = HdlFsmDiagramDoc,
)

Session.registerDocType(DOC_TYPE)
