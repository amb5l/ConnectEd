# place holder for future FSM Diagram document
from ..core.session import Session
from ..core.doc     import Doc


class HdlFsmDiagramDoc(Doc):
    pass


Session.registerDocType(
    "HDL FSM Diagram",   # friendly document type name
    "HDL FSM Diagrams",  # friendly document group name
    ".hdl_fsm",          # file extension
    "HdlFsmDiagram",     # XML tag
    HdlFsmDiagramDoc     # class
)
