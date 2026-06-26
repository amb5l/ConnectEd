from __future__ import annotations

from ..core.session import DocType, Session
from ..core.doc     import Doc


class HdlFsmDiagramDoc(Doc):
    _XML_TAG = "HdlFsmDiagram"


DOC_TYPE = DocType(
    name  = "HDL FSM Diagram",
    group = "HDL FSM Diagrams",
    ext   = "hdl_fsm",
    cls   = HdlFsmDiagramDoc,
)

Session.registerDocType(DOC_TYPE)
