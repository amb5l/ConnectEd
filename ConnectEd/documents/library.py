from ..core.session import Session
from ..core.doc     import Doc

class HdlSchematicLibraryDoc(Doc):
    pass


Session.registerDocType(
    "HDL Schematic Library",    # friendly document type name
    "HDL Schematic Libraries",  # friendly document group name
    ".hdl_lib",                 # file extension
    "HdlSchematicLibrary",      # XML tag
    HdlSchematicLibraryDoc      # class
)
