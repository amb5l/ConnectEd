from .vhdl_model import VhdlArchitecture             as VhdlArchitecture
from .vhdl_model import VhdlArchitecturesContainer   as VhdlArchitecturesContainer
from .vhdl_model import VhdlComponent                as VhdlComponent
from .vhdl_model import VhdlContainer                as VhdlContainer
from .vhdl_model import VhdlDocument                 as VhdlDocument
from .vhdl_model import VhdlEntitiesContainer        as VhdlEntitiesContainer
from .vhdl_model import VhdlEntity                   as VhdlEntity
from .vhdl_model import VhdlGeneric                  as VhdlGeneric
from .vhdl_model import VhdlItemWithComponentsMixin  as VhdlItemWithComponentsMixin
from .vhdl_model import VhdlItemWithDatatypeMixin    as VhdlItemWithDatatypeMixin
from .vhdl_model import VhdlItemWithDefaultMixin     as VhdlItemWithDefaultMixin
from .vhdl_model import VhdlItemWithModeMixin        as VhdlItemWithModeMixin
from .vhdl_model import VhdlItemWithNameMixin        as VhdlItemWithNameMixin
from .vhdl_model import VhdlItemWithNotesMixin       as VhdlItemWithNotesMixin
from .vhdl_model import VhdlPackage                  as VhdlPackage
from .vhdl_model import VhdlPackagesContainer        as VhdlPackagesContainer
from .vhdl_model import VhdlPort                     as VhdlPort
from .vhdl_model import VhdlPortGroup                as VhdlPortGroup


class VHDLSyntaxError(Exception):
    """Exception raised for VHDL syntax errors."""
    pass
